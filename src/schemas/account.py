"""
Account Pydantic schemas.
"""
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from src.schemas.base import BaseSchema, TimestampSchema


AccountType = Literal["card", "bank_account", "cash", "crypto", "investment"]


class AccountBase(BaseSchema):
    """Базовые поля счёта."""
    
    name: str = Field(min_length=1, max_length=255)
    account_type: AccountType
    currency: str = Field(default="RUB", max_length=3)
    bank_name: str | None = Field(None, max_length=255)
    last_four_digits: str | None = Field(None, min_length=4, max_length=4)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    include_in_total: bool = True
    
    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Валидация валюты."""
        allowed = ["RUB", "USD", "EUR", "GBP", "CNY", "BTC", "ETH"]
        if v.upper() not in allowed:
            raise ValueError(f"Currency must be one of: {', '.join(allowed)}")
        return v.upper()


class AccountCreate(AccountBase):
    """Схема создания счёта."""
    
    balance: Decimal = Field(default=Decimal("0.00"), ge=0)


class AccountUpdate(BaseSchema):
    """Схема обновления счёта."""
    
    name: str | None = Field(None, min_length=1, max_length=255)
    account_type: AccountType | None = None
    currency: str | None = Field(None, max_length=3)
    balance: Decimal | None = Field(None, ge=0)
    bank_name: str | None = Field(None, max_length=255)
    last_four_digits: str | None = Field(None, min_length=4, max_length=4)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active: bool | None = None
    include_in_total: bool | None = None


class AccountInDB(AccountBase, TimestampSchema):
    """Счёт из БД."""
    
    id: int
    user_id: int
    balance: Decimal
    is_active: bool


class AccountResponse(AccountBase, TimestampSchema):
    """Счёт для API ответа."""
    
    id: int
    balance: Decimal
    is_active: bool


class AccountWithStats(AccountResponse):
    """Счёт с дополнительной статистикой."""
    
    transaction_count: int = 0
    last_transaction_date: str | None = None
    income_total: Decimal = Decimal("0.00")
    expense_total: Decimal = Decimal("0.00")

