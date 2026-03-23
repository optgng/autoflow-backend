"""Tests for LLM Privacy Layer."""
import pytest
from src.services.llm_privacy import sanitize_for_llm, prepare_batch_for_llm, build_llm_prompt

SALT = b"test_salt_32bytes_padded_to_size!"


class TestSanitizeForLlm:
    def test_person_transfer_replaced(self):
        tx = {"merchant": "Перевод для М. Анна Арменовна", "amount": 5000, "tx_type": "expense"}
        sanitized, token_map = sanitize_for_llm(tx, SALT)
        assert "Анна" not in sanitized["merchant"]
        assert "[PERSON_" in sanitized["merchant"]
        assert len(token_map) == 1

    def test_account_number_replaced(self):
        tx = {"merchant": "Перевод 40817810730852041773", "amount": 100}
        sanitized, token_map = sanitize_for_llm(tx, SALT)
        assert "40817810730852041773" not in sanitized["merchant"]
        assert "[ACCOUNT_" in sanitized["merchant"]

    def test_card_last4_replaced(self):
        tx = {"merchant": "Оплата ****0104", "amount": 500}
        sanitized, token_map = sanitize_for_llm(tx, SALT)
        assert "****0104" not in sanitized["merchant"]
        assert "[CARD_0104]" in sanitized["merchant"]

    def test_phone_replaced(self):
        tx = {"merchant": "Перевод +7 (999) 123-45-67", "amount": 1000}
        sanitized, token_map = sanitize_for_llm(tx, SALT)
        assert "+7 (999) 123-45-67" not in sanitized["merchant"]
        assert "[PHONE_" in sanitized["merchant"]

    def test_blocked_fields_stripped(self):
        tx = {"merchant": "PYATEROCHKA", "amount": 500, "telegram_id": 123456, "account_number": "40817xxx"}
        sanitized, _ = sanitize_for_llm(tx, SALT)
        assert "telegram_id" not in sanitized
        assert "account_number" not in sanitized

    def test_deterministic_tokens(self):
        tx = {"merchant": "Перевод для М. Анна Арменовна", "amount": 100}
        s1, m1 = sanitize_for_llm(tx, SALT)
        s2, m2 = sanitize_for_llm(tx, SALT)
        assert s1["merchant"] == s2["merchant"]

    def test_different_salt_different_token(self):
        tx = {"merchant": "Перевод для М. Анна Арменовна", "amount": 100}
        s1, _ = sanitize_for_llm(tx, b"salt_one_32_bytes_padded_xxxxxxxxx")
        s2, _ = sanitize_for_llm(tx, b"salt_two_32_bytes_padded_xxxxxxxxx")
        assert s1["merchant"] != s2["merchant"]

    def test_no_pii_unchanged(self):
        tx = {"merchant": "PYATEROCHKA", "amount": 350, "tx_type": "expense"}
        sanitized, token_map = sanitize_for_llm(tx, SALT)
        assert sanitized["merchant"] == "PYATEROCHKA"
        assert len(token_map) == 0


class TestPrepareBatch:
    def test_batch_returns_merged_token_map(self):
        txs = [
            {"merchant": "Перевод для М. Анна Арменовна", "amount": 100, "telegram_id": 99},
            {"merchant": "YANDEXGO", "amount": 650},
        ]
        batch, token_map = prepare_batch_for_llm(txs, SALT)
        assert len(batch) == 2
        assert "telegram_id" not in batch[0]
        assert "[PERSON_" in batch[0]["merchant"]
        assert batch[1]["merchant"] == "YANDEXGO"

    def test_build_prompt_contains_merchant(self):
        tx = {"merchant": "PYATEROCHKA", "amount": 350, "tx_type": "expense", "date": "2026-02-13", "bank_category": "Продукты"}
        prompt = build_llm_prompt(tx)
        assert "PYATEROCHKA" in prompt
        assert "350" in prompt
