"""
Transaction Pydantic schemas.
"""
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from src.schemas.account import AccountResponse
from src.schemas.base import BaseSchema, TimestampSchema
from src.schemas.category import CategoryResponse


TransactionType = Literal["income", "expense", "transfer"]

class AccountShort(BaseSchema):
    id: int
    name: str

class CategoryShort(BaseSchema):
    id: int
    name: str


class TransactionBase(BaseSchema):
    """Базовые поля транзакции."""
    
    account_id: int
    category_id: int | None = None
    transaction_date: date
    amount: Decimal = Field(gt=0)
    transaction_type: TransactionType
    description: str | None = Field(None, max_length=500)
    notes: str | None = None
    merchant: str | None = Field(None, max_length=255)
    location: str | None = Field(None, max_length=255)
    tags: str | None = Field(None, max_length=500)
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: str | None) -> str | None:
        """Валидация тегов (comma-separated)."""
        if v is None:
            return None
        # Удаляем лишние пробелы
        tags = [tag.strip() for tag in v.split(",")]
        return ", ".join([tag for tag in tags if tag])


class TransactionCreate(TransactionBase):
    """Схема создания транзакции."""
    
    target_account_id: int | None = None
    
    @field_validator("target_account_id")
    @classmethod
    def validate_transfer(cls, v: int | None, info) -> int | None:
        """Для переводов target_account_id обязателен."""
        if info.data.get("transaction_type") == "transfer" and v is None:
            raise ValueError("target_account_id required for transfer transactions")
        return v


class TransactionUpdate(BaseSchema):
    """Схема обновления транзакции."""
    
    account_id: int | None = None
    category_id: int | None = None
    transaction_date: date | None = None
    amount: Decimal | None = Field(None, gt=0)
    transaction_type: TransactionType | None = None
    description: str | None = Field(None, max_length=500)
    notes: str | None = None
    merchant: str | None = Field(None, max_length=255)
    location: str | None = Field(None, max_length=255)
    tags: str | None = Field(None, max_length=500)
    target_account_id: int | None = None


class TransactionInDB(TransactionBase, TimestampSchema):
    """Транзакция из БД."""
    
    id: int
    target_account_id: int | None


class TransactionResponse(TransactionBase, TimestampSchema):
    """Транзакция для API ответа."""
    
    id: int
    target_account_id: int | None
    account: AccountShort | None = None      # ← добавить
    category: CategoryShort | None = None


class TransactionDetail(TransactionResponse):
    """Детальная транзакция с relationships."""
    
    account: AccountResponse
    category: CategoryResponse | None = None
    target_account: AccountResponse | None = None


class TransactionFilters(BaseSchema):
    """Фильтры для поиска транзакций."""
    
    account_id: int | None = None
    category_id: int | None = None
    transaction_type: TransactionType | None = None
    date_from: date | None = None
    date_to: date | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    merchant: str | None = None
    search: str | None = None  # Поиск по description

