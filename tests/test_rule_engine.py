"""Tests for Rule Engine."""
import pytest
from src.services.rule_engine import apply_rules


class TestRuleEngine:
    def test_internal_transfer_vklad_karta(self):
        tx = {"merchant": "VKLAD-KARTA", "tx_type": "expense", "amount": 50000}
        result = apply_rules(tx)
        assert result is not None
        assert result["enriched_category"] == "Внутренний перевод"
        assert result["exclude_from_metrics"] is True

    def test_internal_transfer_kopilka(self):
        tx = {"merchant": "KOPILKA auto", "tx_type": "expense", "amount": 10000}
        result = apply_rules(tx)
        assert result["enriched_category"] == "Внутренний перевод"

    def test_salary(self):
        tx = {"merchant": "Заработная плата за февраль", "tx_type": "income", "amount": 150000}
        result = apply_rules(tx)
        assert result["enriched_category"] == "Зарплата"
        assert result["income_type"] == "operational"

    def test_salary_wrong_type_not_matched(self):
        tx = {"merchant": "Заработная плата", "tx_type": "expense", "amount": 1000}
        result = apply_rules(tx)
        assert result is None or result.get("enriched_category") != "Зарплата"

    def test_subscription_spotify(self):
        tx = {"merchant": "SPOTIFY", "tx_type": "expense", "amount": 199}
        result = apply_rules(tx)
        assert result["enriched_category"] == "Подписки"
        assert result["expense_type"] == "subscription"

    def test_taxi_yandex_go(self):
        tx = {"merchant": "YANDEX*GO", "tx_type": "expense", "amount": 750}
        result = apply_rules(tx)
        assert result["enriched_category"] == "Такси"

    def test_cashback(self):
        tx = {"merchant": "Кэшбэк по карте", "tx_type": "income", "amount": 500}
        result = apply_rules(tx)
        assert result["enriched_category"] == "Кэшбэк"
        assert result["exclude_from_metrics"] is True

    def test_no_match_returns_none(self):
        tx = {"merchant": "UNKNOWN_MERCHANT_XYZ", "tx_type": "expense", "amount": 100}
        result = apply_rules(tx)
        assert result is None
