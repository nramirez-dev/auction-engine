import os
from typing import AsyncGenerator
from redis import asyncio as aioredis

class RedisClient:
    """Singleton for managing the async Redis connection pool."""
    _instance = None
    _client: aioredis.Redis | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """Initializes the Redis connection pool."""
        if self._client is None:
            host = os.getenv("REDIS_HOST", "localhost")
            port = os.getenv("REDIS_PORT", "6379")
            password = os.getenv("REDIS_PASS", None)
            
            self._client = aioredis.from_url(
                f"redis://{host}:{port}",
                password=password,
                decode_responses=True
            )

    async def disconnect(self) -> None:
        """Closes the Redis connection pool."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> aioredis.Redis:
        if not self._client:
            raise RuntimeError("Redis client is not connected.")
        return self._client


redis_manager = RedisClient()

async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """Dependency injection generator for FastAPI."""
    yield redis_manager.client

