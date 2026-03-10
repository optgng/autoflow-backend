"""
Database models.
"""
from src.models.base import Base

# Базовые модели сначала (без зависимостей)
from src.models.user import User
from src.models.account import Account
from src.models.category import Category  # убедитесь, что есть и импортируется

# Dependent модели после
from src.models.budget import Budget
from src.models.transaction import Transaction
from src.models.legacy import LegacyAccount, LegacyTransaction, LegacyUser

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

