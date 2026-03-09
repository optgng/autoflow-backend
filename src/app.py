"""
FastAPI application factory.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.router import api_router
from src.config import settings
from src.core.cache import cache
from src.core.database import close_db, init_db
from src.core.exceptions import AutoFlowException
from src.core.logging import get_logger, setup_logging

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    logger.info("Starting AutoFlow Backend", version=settings.APP_VERSION)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Connect to Redis
    await cache.connect()
    logger.info("Redis connected")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AutoFlow Backend")
    await cache.disconnect()
    await close_db()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )
    
    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Exception handler for custom exceptions
    @app.exception_handler(AutoFlowException)
    async def autoflow_exception_handler(
        request: Request, exc: AutoFlowException
    ) -> JSONResponse:
        """Handle custom AutoFlow exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "error_data": exc.detail,
            },
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
    
    # Include API routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    
    return app


# Create app instance
app = create_app()

