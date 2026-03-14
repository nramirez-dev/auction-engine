import json
from typing import AsyncGenerator
from uuid import UUID
from redis import asyncio as aioredis

from src.domain.bid import Bid
from src.domain.interfaces import IBroadcastService


class WebSocketBroadcaster(IBroadcastService):
    def __init__(self, redis_client: aioredis.Redis):
        self._redis = redis_client

    async def publish(self, auction_id: UUID, bid: Bid) -> None:
        payload = {
            "auction_id": str(bid.auction_id),
            "user_id": str(bid.user_id),
            "amount": float(bid.amount),
            "placed_at": bid.placed_at.isoformat()
        }
        
        channel = f"auction:{auction_id}"
        await self._redis.publish(channel, json.dumps(payload))

    async def subscribe(self, auction_id: UUID) -> AsyncGenerator[dict, None]:
        channel = f"auction:{auction_id}"
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield json.loads(message["data"])
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
