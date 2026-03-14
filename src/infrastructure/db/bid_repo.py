import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.product import Product
from src.domain.auction import Auction
from src.domain.bid import Bid
from src.domain.interfaces import IBidRepository, IProductRepository, IAuctionRepository
from src.domain.exceptions import ProductNotFoundException, AuctionNotFoundException
from src.infrastructure.db.models import ProductModel, AuctionModel, BidModel

class BidRepository(IBidRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, bid: Bid) -> Bid:
        bid_model = BidModel(
            id=bid.id,
            auction_id=bid.auction_id,
            user_id=bid.user_id,
            amount=bid.amount,
            placed_at=bid.placed_at,
            idempotency_key=bid.idempotency_key
        )
        self.session.add(bid_model)
        await self.session.commit()
        return bid

    async def exists_by_idempotency_key(self, key: str) -> bool:
        stmt = select(BidModel).where(BidModel.idempotency_key == key)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None


class ProductRepository(IProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: ProductModel) -> Product:
        return Product(
            id=model.id,
            owner_id=model.owner_id,
            title=model.title,
            starting_price=model.starting_price,
            created_at=model.created_at,
            description=model.description
        )

    async def save(self, product: Product) -> Product:
        product_model = ProductModel(
            id=product.id,
            owner_id=product.owner_id,
            title=product.title,
            starting_price=product.starting_price,
            created_at=product.created_at,
            description=product.description
        )
        self.session.add(product_model)
        await self.session.commit()
        return product

    async def get_by_id(self, id: uuid.UUID) -> Product:
        result = await self.session.execute(select(ProductModel).where(ProductModel.id == id))
        model = result.scalars().first()
        if not model:
            raise ProductNotFoundException(id)
        return self._to_domain(model)

    async def delete(self, id: uuid.UUID) -> None:
        result = await self.session.execute(select(ProductModel).where(ProductModel.id == id))
        model = result.scalars().first()
        if not model:
            raise ProductNotFoundException(id)
        await self.session.delete(model)
        await self.session.commit()

    async def get_all(self) -> list[Product]:
        result = await self.session.execute(select(ProductModel))
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]


class AuctionRepository(IAuctionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: AuctionModel) -> Auction:
        return Auction(
            id=model.id,
            product_id=model.product_id,
            status=model.status,
            current_price=model.current_price,
            started_at=model.started_at,
            winner_id=model.winner_id,
            closed_at=model.closed_at
        )

    async def save(self, auction: Auction) -> Auction:
        auction_model = AuctionModel(
            id=auction.id,
            product_id=auction.product_id,
            status=auction.status,
            current_price=auction.current_price,
            started_at=auction.started_at,
            winner_id=auction.winner_id,
            closed_at=auction.closed_at
        )
        self.session.add(auction_model)
        await self.session.commit()
        return auction

    async def get_by_id(self, id: uuid.UUID) -> Auction:
        result = await self.session.execute(select(AuctionModel).where(AuctionModel.id == id))
        model = result.scalars().first()
        if not model:
            raise AuctionNotFoundException(id)
        return self._to_domain(model)

    async def get_by_product_id(self, product_id: uuid.UUID) -> Auction:
        result = await self.session.execute(select(AuctionModel).where(AuctionModel.product_id == product_id))
        model = result.scalars().first()
        if not model:
            raise AuctionNotFoundException(product_id)
        return self._to_domain(model)

    async def update_price(self, auction_id: uuid.UUID, new_price: Decimal, winner_id: uuid.UUID) -> None:
        result = await self.session.execute(select(AuctionModel).where(AuctionModel.id == auction_id))
        model = result.scalars().first()
        if not model:
            raise AuctionNotFoundException(auction_id)
        model.current_price = new_price
        model.winner_id = winner_id
        await self.session.commit()

