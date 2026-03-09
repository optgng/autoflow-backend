"""
Redis cache wrapper.
"""
import json
from typing import Any

from redis.asyncio import Redis

from src.config import settings


class RedisCache:
    """Async Redis cache wrapper."""

    def __init__(self) -> None:
        self.redis: Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self.redis = Redis.from_url(
            str(settings.REDIS_URL),
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Any:
        """Get value from cache."""
        if not self.redis:
            return None
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL) -> None:
        """Set value in cache with TTL."""
        if not self.redis:
            return
        await self.redis.setex(key, ttl, json.dumps(value, default=str))

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        if not self.redis:
            return
        await self.redis.delete(key)


cache = RedisCache()

