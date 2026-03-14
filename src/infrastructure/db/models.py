import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Numeric, String, Enum, ForeignKey, func, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.domain.auction import AuctionStatus

class Base(DeclarativeBase):
    pass

class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    starting_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)

    auctions: Mapped[list["AuctionModel"]] = relationship("AuctionModel", back_populates="product", cascade="all, delete-orphan")


class AuctionModel(Base):
    __tablename__ = "auctions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    status: Mapped[AuctionStatus] = mapped_column(Enum(AuctionStatus), nullable=False)
    current_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
    winner_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="auctions")
    bids: Mapped[list["BidModel"]] = relationship("BidModel", back_populates="auction", cascade="all, delete-orphan")


class BidModel(Base):
    __tablename__ = "bids"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auctions.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    placed_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True)

    auction: Mapped["AuctionModel"] = relationship("AuctionModel", back_populates="bids")

