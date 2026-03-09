"""
Dashboard Pydantic schemas.
"""
from datetime import date
from decimal import Decimal

from src.schemas.account import AccountResponse
from src.schemas.base import BaseSchema
from src.schemas.transaction import TransactionResponse


class BalanceOverview(BaseSchema):
    """Обзор баланса."""
    
    total_balance: Decimal
    currency: str = "RUB"
    change_amount: Decimal = Decimal("0.00")
    change_percentage: float = 0.0
    account_count: int = 0


class IncomeExpenseSummary(BaseSchema):
    """Сводка доходов/расходов."""
    
    total_income: Decimal = Decimal("0.00")
    total_expense: Decimal = Decimal("0.00")
    net_amount: Decimal = Decimal("0.00")
    income_count: int = 0
    expense_count: int = 0


class CategorySummary(BaseSchema):
    """Сводка по категории."""
    
    category_id: int
    category_name: str
    category_type: str
    total_amount: Decimal
    transaction_count: int
    percentage: float = 0.0


class MonthlyComparison(BaseSchema):
    """Сравнение по месяцам."""
    
    month: str  # YYYY-MM
    income: Decimal
    expense: Decimal
    net: Decimal


class DashboardData(BaseSchema):
    """Полные данные для дашборда."""
    
    period_start: date
    period_end: date
    
    balance: BalanceOverview
    income_expense: IncomeExpenseSummary
    
    top_accounts: list[AccountResponse]
    recent_transactions: list[TransactionResponse]
    
    expense_by_category: list[CategorySummary]
    income_by_category: list[CategorySummary]
    
    monthly_trend: list[MonthlyComparison]

