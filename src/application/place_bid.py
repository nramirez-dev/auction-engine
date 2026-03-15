import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)

from src.domain.auction import AuctionStatus
from src.domain.bid import Bid
from src.domain.interfaces import IBidRepository, IAuctionRepository, ILockService, IBroadcastService
from src.domain.exceptions import (
    AuctionNotFoundException,
    AuctionNotActiveException,
    BidTooLowException,
    DuplicateBidException
)

class PlaceBidUseCase:
    """Use case for processing a new bid on a specific auction."""

    def __init__(
        self,
        bid_repo: IBidRepository,
        auction_repo: IAuctionRepository,
        lock_service: ILockService,
        broadcast_service: IBroadcastService
    ):
        self._bid_repo = bid_repo
        self._auction_repo = auction_repo
        self._lock_service = lock_service
        self._broadcast_service = broadcast_service

    async def execute(self, auction_id: uuid.UUID, user_id: uuid.UUID, amount: Decimal, idempotency_key: Optional[str] = None) -> Bid:
        if idempotency_key:
            if await self._bid_repo.exists_by_idempotency_key(idempotency_key):
                raise DuplicateBidException(idempotency_key)

        async with self._lock_service.acquire(f"auction:{auction_id}"):
            auction = await self._auction_repo.get_by_id(auction_id)
            if not auction:
                raise AuctionNotFoundException(auction_id)
            
            if auction.status != AuctionStatus.ACTIVE:
                raise AuctionNotActiveException(auction_id, auction.status.value)
                
            if amount <= auction.current_price:
                raise BidTooLowException(auction.current_price, amount)
                
            bid = Bid(
                id=uuid.uuid4(),
                auction_id=auction_id,
                user_id=user_id,
                amount=amount,
                placed_at=datetime.now(timezone.utc),
                idempotency_key=idempotency_key
            )
            
            saved_bid = await self._bid_repo.save(bid)
            await self._auction_repo.update_price(auction_id, amount, user_id)

            try:
                await self._broadcast_service.publish(auction_id, saved_bid)
            except Exception as exc:
                logger.warning(
                    "Broadcast failed for auction %s bid %s — clients will not receive real-time update: %s",
                    auction_id, saved_bid.id, exc
                )

            return saved_bid

