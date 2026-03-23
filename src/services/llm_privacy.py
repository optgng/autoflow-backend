"""LLM Privacy Layer — sanitizes PII before sending to LLM."""
import hmac
import hashlib
import re
from typing import Any

PATTERNS: dict[str, str] = {
    "person_transfer": r"Перевод (?:для|от) ([А-ЯЁ]\.\s[А-ЯЁ][а-яё]+(?:\s[А-ЯЁ][а-яё]+)?)",
    "account_number": r"\b(\d{16,20})\b",
    "card_last4": r"\*{2,4}(\d{4})",
    "phone": r"(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",
    "full_name": r"\b([А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+)\b",
}

LLM_ALLOWED_FIELDS = {"date", "amount", "tx_type", "bank_category", "merchant", "balance"}
LLM_BLOCKED_FIELDS = {"telegram_id", "account_number", "auth_code", "user_id", "hashed_password"}


def _hmac_token(value: str, salt: bytes, prefix: str) -> str:
    """Deterministic 4-char HMAC token for a given value + salt."""
    digest = hmac.new(salt, value.lower().strip().encode(), hashlib.sha256).hexdigest()
    return f"[{prefix}_{digest[:4]}]"


def sanitize_for_llm(transaction: dict, user_salt: bytes) -> tuple[dict, dict]:
    """
    Replace PII in transaction with deterministic tokens.
    Returns (sanitized_tx, token_map).
    token_map is keyed by token string -> original value (session-only, never persisted).
    """
    token_map: dict[str, str] = {}
    sanitized = {k: v for k, v in transaction.items() if k in LLM_ALLOWED_FIELDS}

    merchant: str = sanitized.get("merchant") or ""

    # person_transfer — named groups
    def replace_person_transfer(m: re.Match) -> str:
        name = m.group(1)
        token = _hmac_token(name, user_salt, "PERSON")
        token_map[token] = name
        return m.group(0).replace(name, token)

    merchant = re.sub(PATTERNS["person_transfer"], replace_person_transfer, merchant)

    # full_name (ФИО) — standalone
    def replace_full_name(m: re.Match) -> str:
        name = m.group(1)
        token = _hmac_token(name, user_salt, "PERSON")
        token_map[token] = name
        return token

    merchant = re.sub(PATTERNS["full_name"], replace_full_name, merchant)

    # account_number
    def replace_account(m: re.Match) -> str:
        acc = m.group(1)
        token = _hmac_token(acc, user_salt, "ACCOUNT")
        token_map[token] = acc
        return token

    merchant = re.sub(PATTERNS["account_number"], replace_account, merchant)

    # card_last4
    def replace_card(m: re.Match) -> str:
        last4 = m.group(1)
        token = f"[CARD_{last4}]"
        token_map[token] = m.group(0)
        return token

    merchant = re.sub(PATTERNS["card_last4"], replace_card, merchant)

    # phone
    def replace_phone(m: re.Match) -> str:
        phone = m.group(0)
        token = _hmac_token(phone, user_salt, "PHONE")
        token_map[token] = phone
        return token

    merchant = re.sub(PATTERNS["phone"], replace_phone, merchant)

    sanitized["merchant"] = merchant
    return sanitized, token_map


def prepare_batch_for_llm(
    transactions: list[dict], user_salt: bytes
) -> tuple[list[dict], dict]:
    """
    Sanitize a list of transactions for LLM.
    Returns (sanitized_list, merged_token_map).
    """
    result: list[dict] = []
    merged_token_map: dict[str, str] = {}

    for tx in transactions:
        # Strip blocked fields first
        clean_tx = {k: v for k, v in tx.items() if k not in LLM_BLOCKED_FIELDS}
        sanitized, token_map = sanitize_for_llm(clean_tx, user_salt)
        merged_token_map.update(token_map)
        result.append(sanitized)

    return result, merged_token_map


LLM_SYSTEM_PROMPT = """You are a financial transaction classifier. You receive sanitized transaction data where personal identifiers have been replaced with tokens like [PERSON_xxxx], [ACCOUNT_xxxx].
DO NOT attempt to reconstruct or guess the original values behind these tokens.
Classify each transaction based only on merchant name patterns and amount context.

Respond ONLY with valid JSON. No explanations, no markdown blocks."""

LLM_USER_PROMPT_TEMPLATE = """Classify the following transaction:
{{
  "date": "{date}",
  "amount": {amount},
  "tx_type": "{tx_type}",
  "bank_category": "{bank_category}",
  "merchant": "{merchant}"
}}

Respond with:
{{
  "enriched_category": "<category from list>",
  "income_type": "<operational|oneoff|return|internal|null>",
  "expense_type": "<regular|subscription|oneoff|investment|debt_payment|null>",
  "is_internal_transfer": <true|false>,
  "exclude_from_metrics": <true|false>,
  "is_group_payment_suspect": <true|false>,
  "confidence": <0.0-1.0>,
  "needs_user_review": <true|false>,
  "review_reason": "<short reason or null>"
}}

Allowed enriched_category values:
"Зарплата", "Фриланс", "Возврат", "Кэшбэк", "Продукты", "Рестораны",
"Транспорт", "Такси", "Подписки", "Связь", "Одежда", "Здоровье",
"Развлечения", "Путешествия", "Обязательные платежи", "Переводы (регулярные)",
"Переводы (долги)", "Инвестиции", "Внутренний перевод", "Донаты", "Прочее"
"""


def build_llm_prompt(sanitized_tx: dict) -> str:
    return LLM_USER_PROMPT_TEMPLATE.format(
        date=sanitized_tx.get("date", ""),
        amount=sanitized_tx.get("amount", 0),
        tx_type=sanitized_tx.get("tx_type", ""),
        bank_category=sanitized_tx.get("bank_category", ""),
        merchant=sanitized_tx.get("merchant", ""),
    )
