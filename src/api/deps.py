from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.infrastructure.db.session import get_db
from src.infrastructure.redis.client import get_redis
from src.infrastructure.db.bid_repo import BidRepository, ProductRepository, AuctionRepository
from src.infrastructure.redis.lock_service import LockService
from src.infrastructure.websocket.broadcaster import WebSocketBroadcaster

from src.domain.interfaces import (
    IBidRepository,
    IProductRepository,
    IAuctionRepository,
    ILockService,
    IBroadcastService,
)

from src.application.place_bid import PlaceBidUseCase
from src.application.products import (
    CreateProductUseCase,
    GetProductUseCase,
    DeleteProductUseCase,
    ListProductsUseCase,
)

def get_bid_repository(db: AsyncSession = Depends(get_db)) -> IBidRepository:
    return BidRepository(db)

def get_product_repository(db: AsyncSession = Depends(get_db)) -> IProductRepository:
    return ProductRepository(db)

def get_auction_repository(db: AsyncSession = Depends(get_db)) -> IAuctionRepository:
    return AuctionRepository(db)

def get_lock_service(redis: Redis = Depends(get_redis)) -> ILockService:
    return LockService(redis)

def get_broadcast_service(redis: Redis = Depends(get_redis)) -> IBroadcastService:
    return WebSocketBroadcaster(redis)

def get_place_bid_use_case(
    bid_repo: IBidRepository = Depends(get_bid_repository),
    auction_repo: IAuctionRepository = Depends(get_auction_repository),
    lock_service: ILockService = Depends(get_lock_service),
    broadcast_service: IBroadcastService = Depends(get_broadcast_service),
) -> PlaceBidUseCase:
    return PlaceBidUseCase(bid_repo, auction_repo, lock_service, broadcast_service)

def get_create_product_use_case(
    product_repo: IProductRepository = Depends(get_product_repository),
) -> CreateProductUseCase:
    return CreateProductUseCase(product_repo)

def get_get_product_use_case(
    product_repo: IProductRepository = Depends(get_product_repository),
) -> GetProductUseCase:
    return GetProductUseCase(product_repo)

def get_delete_product_use_case(
    product_repo: IProductRepository = Depends(get_product_repository),
) -> DeleteProductUseCase:
    return DeleteProductUseCase(product_repo)

def get_list_products_use_case(
    product_repo: IProductRepository = Depends(get_product_repository),
) -> ListProductsUseCase:
    return ListProductsUseCase(product_repo)
