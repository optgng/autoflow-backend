"""
Database models.
"""
from src.models.account import Account
from src.models.base import Base
from src.models.budget import Budget
from src.models.category import Category
from src.models.legacy import LegacyAccount, LegacyTransaction, LegacyUser
from src.models.transaction import Transaction
from src.models.user import User

__all__ = [
    "Base",
    # Новые модели (finances schema)
    "User",
    "Account",
    "Category",
    "Transaction",
    "Budget",
    # Legacy модели (finance schema, read-only)
    "LegacyUser",
    "LegacyAccount",
    "LegacyTransaction",
]

