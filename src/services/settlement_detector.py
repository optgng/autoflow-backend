"""Mutual settlement detection between transfer pairs."""
import hashlib
import hmac
import re
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

TRANSFER_PATTERN = re.compile(
    r"Перевод (?:для|от) ([А-ЯЁ]\.[\s][А-ЯЁ][а-яё]+(?:\s[А-ЯЁ][а-яё]+)?)"
)


@dataclass
class SettlementPair:
    expense_tx_id: int
    income_tx_id: int
    contact_ref: str
    net_amount: Decimal


def _contact_ref(name: str, user_salt: bytes) -> str:
    digest = hmac.new(user_salt, name.lower().strip().encode(), hashlib.sha256).hexdigest()
    return f"cnt_{digest[:16]}"


def extract_contact_ref(merchant: str, user_salt: bytes) -> str | None:
    m = TRANSFER_PATTERN.search(merchant or "")
    if m:
        return _contact_ref(m.group(1), user_salt)
    return None


def detect_settlements(
    transactions: list[dict],
    user_salt: bytes,
) -> list[SettlementPair]:
    """
    Find expense+income pairs with same contact_ref within ±7 days.
    Mutates transactions dicts: sets 'contact_ref'.
    """
    # Attach contact_ref to each tx
    for tx in transactions:
        ref = extract_contact_ref(tx.get("merchant", ""), user_salt)
        if ref:
            tx["contact_ref"] = ref

    expenses = [
        tx for tx in transactions
        if tx.get("tx_type") == "expense" and tx.get("contact_ref")
    ]
    incomes = [
        tx for tx in transactions
        if tx.get("tx_type") == "income" and tx.get("contact_ref")
    ]

    pairs: list[SettlementPair] = []
    used_income_ids: set[int] = set()

    for exp in expenses:
        exp_date = date.fromisoformat(exp["date"]) if isinstance(exp["date"], str) else exp["date"]
        for inc in incomes:
            if inc["id"] in used_income_ids:
                continue
            if inc.get("contact_ref") != exp.get("contact_ref"):
                continue
            inc_date = date.fromisoformat(inc["date"]) if isinstance(inc["date"], str) else inc["date"]
            if abs((inc_date - exp_date).days) <= 7:
                net = Decimal(str(inc["amount"])) - Decimal(str(exp["amount"]))
                pairs.append(
                    SettlementPair(
                        expense_tx_id=exp["id"],
                        income_tx_id=inc["id"],
                        contact_ref=exp["contact_ref"],
                        net_amount=net,
                    )
                )
                used_income_ids.add(inc["id"])
                break

    return pairs
