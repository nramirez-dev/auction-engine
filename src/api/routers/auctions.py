import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.schemas.auction import CreateAuctionRequest, AuctionResponse
from src.application.auctions import CreateAuctionUseCase, GetAuctionUseCase
from src.api.deps import get_create_auction_use_case, get_get_auction_use_case

router = APIRouter(prefix="/auctions", tags=["Auctions"])

@router.post("", response_model=AuctionResponse, status_code=status.HTTP_201_CREATED)
async def create_auction(
    request: CreateAuctionRequest,
    use_case: CreateAuctionUseCase = Depends(get_create_auction_use_case),
):
    """
    Creates a new auction.
    """
    auction = await use_case.execute(request.product_id, request.owner_id)
    return auction

@router.get("/{auction_id}", response_model=AuctionResponse, status_code=status.HTTP_200_OK)
async def get_auction(
    auction_id: uuid.UUID,
    use_case: GetAuctionUseCase = Depends(get_get_auction_use_case),
):
    """
    Retrieves a specific auction by ID.
    """
    auction = await use_case.execute(auction_id)
    return auction
