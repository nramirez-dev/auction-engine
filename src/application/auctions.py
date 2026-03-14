import uuid
from datetime import datetime, timezone

from src.domain.auction import Auction, AuctionStatus
from src.domain.interfaces import IAuctionRepository, IProductRepository
from src.domain.exceptions import ProductNotFoundException, UnauthorizedProductAccessException, AuctionNotFoundException

class CreateAuctionUseCase:
    """Use case for creating a new auction based on an existing product."""

    def __init__(self, auction_repo: IAuctionRepository, product_repo: IProductRepository):
        self._auction_repo = auction_repo
        self._product_repo = product_repo
        
    async def execute(self, product_id: uuid.UUID, owner_id: uuid.UUID) -> Auction:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
            
        if product.owner_id != owner_id:
            raise UnauthorizedProductAccessException(owner_id, product_id)
            
        auction = Auction(
            id=uuid.uuid4(),
            product_id=product_id,
            status=AuctionStatus.ACTIVE,
            current_price=product.starting_price,
            started_at=datetime.now(timezone.utc)
        )
        return await self._auction_repo.save(auction)

class GetAuctionUseCase:
    """Use case for retrieving a single auction by its ID."""

    def __init__(self, auction_repo: IAuctionRepository):
        self._auction_repo = auction_repo
        
    async def execute(self, auction_id: uuid.UUID) -> Auction:
        auction = await self._auction_repo.get_by_id(auction_id)
        if not auction:
            raise AuctionNotFoundException(auction_id)
        return auction
