"""Tests for Settlement Detector."""
import pytest
from src.services.settlement_detector import detect_settlements, extract_contact_ref

SALT = b"test_salt_32bytes_padded_to_size!"


class TestContactRef:
    def test_extracts_ref_from_merchant(self):
        ref = extract_contact_ref("Перевод для М. Иван Иванович", SALT)
        assert ref is not None
        assert ref.startswith("cnt_")
        assert len(ref) == 20  # cnt_ + 16 hex chars

    def test_no_match_returns_none(self):
        ref = extract_contact_ref("PYATEROCHKA", SALT)
        assert ref is None

    def test_deterministic(self):
        r1 = extract_contact_ref("Перевод для М. Иван Иванович", SALT)
        r2 = extract_contact_ref("Перевод для М. Иван Иванович", SALT)
        assert r1 == r2


class TestDetectSettlements:
    def test_finds_expense_income_pair(self):
        txs = [
            {"id": 1, "merchant": "Перевод для М. Иван Иванович", "tx_type": "expense", "amount": 5000, "date": "2026-02-10"},
            {"id": 2, "merchant": "Перевод от М. Иван Иванович", "tx_type": "income", "amount": 5000, "date": "2026-02-12"},
        ]
        pairs = detect_settlements(txs, SALT)
        assert len(pairs) == 1
        assert pairs[0].expense_tx_id == 1
        assert pairs[0].income_tx_id == 2

    def test_no_pair_outside_window(self):
        txs = [
            {"id": 1, "merchant": "Перевод для М. Иван Иванович", "tx_type": "expense", "amount": 5000, "date": "2026-02-01"},
            {"id": 2, "merchant": "Перевод от М. Иван Иванович", "tx_type": "income", "amount": 5000, "date": "2026-02-20"},
        ]
        pairs = detect_settlements(txs, SALT)
        assert len(pairs) == 0

    def test_different_contacts_no_pair(self):
        txs = [
            {"id": 1, "merchant": "Перевод для М. Иван Иванович", "tx_type": "expense", "amount": 3000, "date": "2026-02-10"},
            {"id": 2, "merchant": "Перевод от П. Пётр Петрович", "tx_type": "income", "amount": 3000, "date": "2026-02-11"},
        ]
        pairs = detect_settlements(txs, SALT)
        assert len(pairs) == 0
