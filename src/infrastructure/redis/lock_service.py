import uuid
from contextlib import asynccontextmanager
from typing import AsyncContextManager, AsyncGenerator
from redis import asyncio as aioredis
from redis.exceptions import LockError

from src.domain.interfaces import ILockService
from src.domain.exceptions import AuctionNotActiveException


class LockService(ILockService):
    """Concrete implementation of ILockService using Redis distributed locks."""

    def __init__(self, redis_client: aioredis.Redis):
        self._redis = redis_client

    @asynccontextmanager
    async def acquire(self, resource_id: str) -> AsyncGenerator[None, None]:
        auction_id_str = resource_id.split(':')[-1]
        try:
            auction_uuid = uuid.UUID(auction_id_str)
        except ValueError:
            auction_uuid = uuid.UUID(int=0)

        lock_key = f"lock:auction:{resource_id}"
        
        lock = self._redis.lock(
            lock_key,
            timeout=5.0,
            blocking_timeout=3.0
        )
        
        acquired = await lock.acquire()
        if not acquired:
            raise AuctionNotActiveException(auction_uuid, "LOCKED")
            
        try:
            yield
        finally:
            try:
                await lock.release()
            except LockError:
                # Lock might have naturally expired, ignore release errors
                pass

