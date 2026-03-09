"""
Pydantic schemas for API validation and serialization.
"""
from src.schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    AccountWithStats,
)
from src.schemas.analytics import AnalyticsReport, CategoryAnalytics, TimeSeriesPoint
from src.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, Token
from src.schemas.base import PaginatedResponse, PaginationParams
from src.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate, BudgetWithStats
from src.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from src.schemas.dashboard import DashboardData, BalanceOverview, IncomeExpenseSummary
from src.schemas.transaction import (
    TransactionCreate,
    TransactionDetail,
    TransactionFilters,
    TransactionResponse,
    TransactionUpdate,
)
from src.schemas.user import UserCreate, UserProfile, UserResponse, UserUpdate

__all__ = [
    # Base
    "PaginationParams",
    "PaginatedResponse",
    # Auth
    "Token",
    "LoginRequest",
    "RegisterRequest",
    "AuthResponse",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    # Account
    "AccountCreate",
    "AccountUpdate",
    "AccountResponse",
    "AccountWithStats",
    # Category
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    # Transaction
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    "TransactionDetail",
    "TransactionFilters",
    # Budget
    "BudgetCreate",
    "BudgetUpdate",
    "BudgetResponse",
    "BudgetWithStats",
    # Dashboard
    "DashboardData",
    "BalanceOverview",
    "IncomeExpenseSummary",
    # Analytics
    "AnalyticsReport",
    "CategoryAnalytics",
    "TimeSeriesPoint",
]

