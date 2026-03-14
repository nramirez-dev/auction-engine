from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status

from src.api.schemas.bid import PlaceBidRequest, PlaceBidResponse
from src.api.deps import get_place_bid_use_case
from src.application.place_bid import PlaceBidUseCase

router = APIRouter(prefix="/place-bid", tags=["bids"])

@router.post("", response_model=PlaceBidResponse, status_code=status.HTTP_201_CREATED)
async def place_bid(
    request: PlaceBidRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    use_case: PlaceBidUseCase = Depends(get_place_bid_use_case),
):
    """
    Places a new bid on a specific auction.
    """
    bid = await use_case.execute(
        auction_id=request.auction_id,
        user_id=request.user_id,
        amount=request.amount,
        idempotency_key=idempotency_key,
    )
    return bid
