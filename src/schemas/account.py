"""
Account Pydantic schemas.
"""
"""
Account Pydantic schemas.
"""
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator, model_validator

from src.schemas.base import BaseSchema, TimestampSchema


AccountType = Literal["card", "bank_account", "cash"]

# Типы, создаваемые только автоимпортом
AUTO_IMPORT_TYPES = ("card", "bank_account")


class AccountBase(BaseSchema):
    """Базовые поля счёта — без ограничительных валидаторов."""

    name:             str         = Field(min_length=1, max_length=255)
    account_type:     AccountType
    currency:         str         = Field(default="RUB", max_length=3)
    bank_name:        str | None  = Field(None, max_length=255)
    last_four_digits: str | None  = Field(None, min_length=4, max_length=4)
    icon:             str | None  = Field(None, max_length=50)
    color:            str | None  = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    include_in_total: bool        = True

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        allowed = ["RUB", "USD", "EUR", "GBP", "CNY", "BTC", "ETH"]
        if v.upper() not in allowed:
            raise ValueError(f"Currency must be one of: {', '.join(allowed)}")
        return v.upper()


class AccountCreate(AccountBase):
    """
    Схема создания счёта.
    Вручную — только cash.
    card/bank_account создаются только через ImportService (минуя этот валидатор).
    """

    balance: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("account_type")
    @classmethod
    def only_cash_allowed(cls, v: AccountType) -> AccountType:
        if v != "cash":
            raise ValueError(
                "Вручную можно создать только счёт наличных. "
                "Банковские карты и счета добавляются автоматически из выписки."
            )
        return v


class AccountUpdate(BaseSchema):
    """
    Схема обновления счёта.

    Разрешено пользователю:
    - name           — все типы
    - currency       — все типы
    - icon, color    — все типы
    - is_active      — все типы
    - include_in_total — все типы
    - bank_name      — только card/bank_account (проверяется в сервисе)
    - account_type   — только card ↔ bank_account (проверяется в сервисе)

    Запрещено (поля отсутствуют):
    - balance        — управляется транзакциями и импортом
    - last_four_digits — системное поле, ставится при импорте
    """

    name:             str | None         = Field(None, min_length=1, max_length=255)
    account_type:     AccountType | None = None
    currency:         str | None         = Field(None, max_length=3)
    bank_name:        str | None         = Field(None, max_length=255)
    icon:             str | None         = Field(None, max_length=50)
    color:            str | None         = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active:        bool | None        = None
    include_in_total: bool | None        = None
    balance: Decimal | None = Field(None, ge=0)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = ["RUB", "USD", "EUR", "GBP", "CNY", "BTC", "ETH"]
        if v.upper() not in allowed:
            raise ValueError(f"Currency must be one of: {', '.join(allowed)}")
        return v.upper()


class AccountInDB(AccountBase, TimestampSchema):
    """Счёт из БД."""

    id:        int
    user_id:   int
    balance:   Decimal
    is_active: bool


class AccountResponse(AccountBase, TimestampSchema):
    """Счёт для API ответа."""

    id:        int
    balance:   Decimal
    is_active: bool


class AccountWithStats(AccountResponse):
    """Счёт с дополнительной статистикой."""

    transaction_count:     int          = 0
    last_transaction_date: str | None   = None
    income_total:          Decimal      = Decimal("0.00")
    expense_total:         Decimal      = Decimal("0.00")

