"""Deterministic rule engine for transaction enrichment."""
from typing import Any, Callable

RuleAction = dict[str, Any]


def _merchant(tx: dict) -> str:
    return (tx.get("merchant") or "").upper()


def _merchant_low(tx: dict) -> str:
    return (tx.get("merchant") or "").lower()


RULES: list[dict] = [
    {
        "id": "T-01",
        "condition": lambda tx: any(
            p in _merchant(tx) for p in ["VKLAD-KARTA", "KARTA-VKLAD", "KOPILKA", "SBER-VKLAD"]
        ),
        "action": {
            "enriched_type": "internal_transfer",
            "enriched_category": "Внутренний перевод",
            "exclude_from_metrics": True,
            "income_type": "internal",
            "expense_type": "internal",
            "review_status": "auto",
        },
    },
    {
        "id": "T-02",
        "condition": lambda tx: (
            any(kw in _merchant_low(tx) for kw in ["заработная плата", "зарплата", "salary"])
            and tx.get("tx_type") == "income"
        ),
        "action": {
            "enriched_category": "Зарплата",
            "income_type": "operational",
            "exclude_from_metrics": False,
            "review_status": "auto",
        },
    },
    {
        "id": "T-03",
        "condition": lambda tx: any(
            p in _merchant(tx)
            for p in ["SPOTIFY", "NETFLIX", "APPSTORE", "GOOGLE*", "YANDEX*PLUS", "YANDEX*MUSIC", "OKKO"]
        ),
        "action": {
            "enriched_category": "Подписки",
            "expense_type": "subscription",
            "exclude_from_metrics": False,
            "review_status": "auto",
        },
    },
    {
        "id": "T-04",
        "condition": lambda tx: any(p in _merchant(tx) for p in ["YANDEX*GO", "YANDEXGO", "UBER", "CITYMOBIL"]),
        "action": {
            "enriched_category": "Такси",
            "expense_type": "oneoff",
            "exclude_from_metrics": False,
            "review_status": "auto",
        },
    },
    {
        "id": "T-05",
        "condition": lambda tx: "автоплатёж" in _merchant_low(tx) or "autoplatezh" in _merchant_low(tx),
        "action": {
            "enriched_category": "Обязательные платежи",
            "expense_type": "regular",
            "exclude_from_metrics": False,
            "review_status": "auto",
        },
    },
    {
        "id": "T-06",
        "condition": lambda tx: (
            any(kw in _merchant_low(tx) for kw in ["кэшбэк", "cashback", "cash back"])
            and tx.get("tx_type") == "income"
        ),
        "action": {
            "enriched_category": "Кэшбэк",
            "income_type": "return",
            "exclude_from_metrics": True,
            "review_status": "auto",
        },
    },
    {
        "id": "T-07",
        "condition": lambda tx: (
            any(kw in _merchant_low(tx) for kw in ["возврат", "refund", "return"])
            and tx.get("tx_type") == "income"
        ),
        "action": {
            "enriched_category": "Возврат",
            "income_type": "return",
            "exclude_from_metrics": False,
            "review_status": "auto",
        },
    },
]


def apply_rules(tx: dict) -> RuleAction | None:
    """Apply rules in priority order. Returns first matching action or None."""
    for rule in RULES:
        try:
            if rule["condition"](tx):
                return dict(rule["action"])
        except Exception:
            continue
    return None
