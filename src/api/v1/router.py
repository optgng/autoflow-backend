"""
Main API v1 router.
"""
from fastapi import APIRouter

from src.api.v1 import accounts, auth, categories, dashboard, transactions

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(accounts.router)
api_router.include_router(categories.router)
api_router.include_router(transactions.router)
api_router.include_router(dashboard.router)

