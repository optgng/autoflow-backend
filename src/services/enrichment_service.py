"""Enrichment orchestrator — runs rule engine + LLM on transactions."""
import asyncio
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.transaction import Transaction
from src.services.llm_privacy import (
    LLM_SYSTEM_PROMPT,
    build_llm_prompt,
    prepare_batch_for_llm,
)
from src.services.rule_engine import apply_rules

logger = logging.getLogger(__name__)

BATCH_SIZE = 20
MAX_RETRIES = 3


async def _call_llm_with_retry(prompt: str) -> dict | None:
    """Call LLM API with exponential backoff. Returns parsed JSON or None."""
    for attempt in range(MAX_RETRIES):
        try:
            if settings.LLM_PROVIDER == "openai":
                result = await _call_openai(prompt)
            elif settings.LLM_PROVIDER == "anthropic":
                result = await _call_anthropic(prompt)
            else:
                return None
            return result
        except Exception as exc:
            wait = 2 ** attempt
            logger.warning("LLM call failed attempt=%d error=%s retry_in=%ds", attempt + 1, type(exc).__name__, wait)
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(wait)
    return None


async def _call_openai(prompt: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": LLM_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)


async def _call_anthropic(prompt: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 512,
                "system": LLM_SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        content = resp.json()["content"][0]["text"]
        return json.loads(content)


async def _get_user_salt(session: AsyncSession, telegram_id: int) -> bytes:
    """Fetch user_salt from user_keys table."""
    from sqlalchemy import text
    result = await session.execute(
        text("SELECT salt FROM finances.user_keys WHERE telegram_id = :tid"),
        {"tid": telegram_id},
    )
    row = result.fetchone()
    if row:
        return bytes.fromhex(row[0]) if isinstance(row[0], str) else row[0]
    # Fallback: derive from secret key (should not happen in production)
    import hmac, hashlib
    return hmac.new(settings.SECRET_KEY.encode(), str(telegram_id).encode(), hashlib.sha256).digest()


async def enrich_transactions(
    session: AsyncSession,
    transactions: list[Transaction],
    telegram_id: int,
) -> None:
    """
    Main enrichment pipeline:
    1. Apply deterministic rule engine
    2. Send unresolved transactions to LLM (batched, privacy-sanitized)
    3. Write enrichment fields back to DB
    """
    if not transactions:
        return

    user_salt = await _get_user_salt(session, telegram_id)

    # Phase 1: Rule engine
    rule_resolved: list[Transaction] = []
    llm_pending: list[Transaction] = []

    for tx in transactions:
        tx_dict = _tx_to_dict(tx)
        rule_result = apply_rules(tx_dict)
        
        if settings.PIPELINE_LOG_VERBOSE:
            logger.info(
                f"[RULE ENGINE] tx_id={tx.id} merchant='{tx.merchant}' "
                f"→ {'MATCH: ' + str(rule_result) if rule_result else 'no match'}"
            )

        if rule_result:
            await _apply_enrichment(session, tx.id, rule_result, source="rule", confidence=Decimal("1.00"))
            rule_resolved.append(tx)
        else:
            llm_pending.append(tx)

    if settings.PIPELINE_LOG_VERBOSE:
        logger.info(f"[PIPELINE] Rule resolved: {len(rule_resolved)}, LLM pending: {len(llm_pending)}")

    # Phase 2: LLM batch
    if not settings.PIPELINE_LLM or not llm_pending:
        if settings.PIPELINE_LOG_VERBOSE and llm_pending:
            logger.info(f"[PIPELINE] LLM disabled, {len(llm_pending)} transactions left unenriched")
        await session.commit()
        return


    for i in range(0, len(llm_pending), BATCH_SIZE):
        batch = llm_pending[i : i + BATCH_SIZE]
        batch_dicts = [_tx_to_dict(tx) for tx in batch]
        sanitized_batch, _ = prepare_batch_for_llm(batch_dicts, user_salt)

        tasks = [_call_llm_with_retry(build_llm_prompt(s)) for s in sanitized_batch]
        results = await asyncio.gather(*tasks)

        for tx, llm_result in zip(batch, results):
            if llm_result:
                confidence = Decimal(str(llm_result.get("confidence", 0.5)))
                review_status = "pending" if llm_result.get("needs_user_review") else "auto"
                enrichment = {
                    "enriched_category": llm_result.get("enriched_category"),
                    "income_type": llm_result.get("income_type"),
                    "expense_type": llm_result.get("expense_type"),
                    "exclude_from_metrics": llm_result.get("exclude_from_metrics", False),
                    "is_group_payment": llm_result.get("is_group_payment_suspect", False),
                    "review_status": review_status,
                }
                # Log only id + confidence — NEVER merchant
                logger.info("enriched transaction_id=%d confidence=%s", tx.id, confidence)
                await _apply_enrichment(session, tx.id, enrichment, source="llm", confidence=confidence)

    await session.commit()


async def _apply_enrichment(
    session: AsyncSession,
    tx_id: int,
    enrichment: dict,
    source: str,
    confidence: Decimal,
) -> None:
    enrichment["enrichment_source"] = source
    enrichment["enrichment_confidence"] = confidence
    enrichment["enriched_at"] = datetime.now(timezone.utc)
    await session.execute(
        update(Transaction).where(Transaction.id == tx_id).values(**enrichment)
    )


def _tx_to_dict(tx: Transaction) -> dict:
    return {
        "id": tx.id,
        "date": str(tx.transaction_date),
        "amount": float(tx.amount),
        "tx_type": tx.transaction_type,
        "bank_category": tx.description or "",
        "merchant": tx.merchant or "",
        "balance": 0,  # balance not stored per-tx in current schema
    }
