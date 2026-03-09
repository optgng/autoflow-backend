"""
Тест подключения к базе данных.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine


async def test_connection():
    # Вставь свой DATABASE_URL сюда
    DATABASE_URL = "postgresql+asyncpg://autoflow_user:abobik123@localhost:7500/finance"
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ Connection successful!")
            print(f"Result: {result.scalar()}")
        await engine.dispose()
    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())

