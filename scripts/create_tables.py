"""
Create all database tables.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import init_db
from src.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


async def main():
    """Create all tables."""
    logger.info("Creating database tables...")
    
    try:
        await init_db()
        logger.info("✅ All tables created successfully!")
    except Exception as e:
        logger.error("❌ Failed to create tables", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())

