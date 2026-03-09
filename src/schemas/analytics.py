"""
Analytics Pydantic schemas.
"""
from datetime import date
from decimal import Decimal
from typing import Literal

from src.schemas.base import BaseSchema


TimeGrouping = Literal["day", "week", "month", "year"]


class TimeSeriesPoint(BaseSchema):
    """Точка временного ряда."""
    
    date: str  # ISO format or period (YYYY-MM)
    income: Decimal = Decimal("0.00")
    expense: Decimal = Decimal("0.00")
    net: Decimal = Decimal("0.00")
    balance: Decimal | None = None


class CategoryAnalytics(BaseSchema):
    """Аналитика по категории."""
    
    category_id: int
    category_name: str
    total_amount: Decimal
    transaction_count: int
    percentage: float
    average_amount: Decimal
    max_amount: Decimal
    min_amount: Decimal


class AccountAnalytics(BaseSchema):
    """Аналитика по счёту."""
    
    account_id: int
    account_name: str
    starting_balance: Decimal
    ending_balance: Decimal
    total_income: Decimal
    total_expense: Decimal
    transaction_count: int


class SpendingPattern(BaseSchema):
    """Паттерн расходов."""
    
    pattern_type: str  # daily_average, weekly_peak, monthly_trend
    value: Decimal
    description: str


class FinancialHealthScore(BaseSchema):
    """Оценка финансового здоровья."""
    
    score: int  # 0-100
    savings_rate: float  # percentage
    expense_volatility: float
    budget_adherence: float
    recommendations: list[str]


class AnalyticsReport(BaseSchema):
    """Полный аналитический отчёт."""
    
    period_start: date
    period_end: date
    
    time_series: list[TimeSeriesPoint]
    
    top_expense_categories: list[CategoryAnalytics]
    top_income_categories: list[CategoryAnalytics]
    
    account_performance: list[AccountAnalytics]
    
    spending_patterns: list[SpendingPattern]
    health_score: FinancialHealthScore

