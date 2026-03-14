from abc import ABC, abstractmethod
from decimal import Decimal
from typing import AsyncContextManager
from uuid import UUID

from src.domain.auction import Auction
from src.domain.bid import Bid
from src.domain.product import Product

class IBidRepository(ABC):
    @abstractmethod
    async def save(self, bid: Bid) -> Bid:
        """Saves a new bid to the data store."""
        pass

    @abstractmethod
    async def exists_by_idempotency_key(self, key: str) -> bool:
        """Checks if a bid with the given idempotency key already exists."""
        pass


class IProductRepository(ABC):
    @abstractmethod
    async def save(self, product: Product) -> Product:
        """Saves a new product or updates an existing one."""
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Product:
        """Retrieves a product by its unique ID."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Deletes a product by its unique ID."""
        pass

    @abstractmethod
    async def get_all(self) -> list[Product]:
        """Retrieves all products."""
        pass


class IAuctionRepository(ABC):
    @abstractmethod
    async def save(self, auction: Auction) -> Auction:
        """Saves a new auction or updates an existing one."""
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Auction:
        """Retrieves an auction by its unique ID."""
        pass

    @abstractmethod
    async def get_by_product_id(self, product_id: UUID) -> Auction:
        """Retrieves an auction associated with a specific product ID."""
        pass

    @abstractmethod
    async def update_price(self, auction_id: UUID, new_price: Decimal, winner_id: UUID) -> None:
        """Updates the current price and winning bidder of an auction."""
        pass


class ILockService(ABC):
    @abstractmethod
    def acquire(self, resource_id: str) -> AsyncContextManager:
        """Acquires a distributed lock for the given resource ID to prevent concurrency issues."""
        pass


class IBroadcastService(ABC):
    @abstractmethod
    async def publish(self, auction_id: UUID, bid: Bid) -> None:
        """Publishes a new bid to all WebSocket subscribers of an auction."""
        pass

