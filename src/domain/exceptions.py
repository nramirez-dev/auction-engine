from decimal import Decimal
from uuid import UUID

class AuctionEngineException(Exception):
    """Base exception for all domain errors."""
    pass

class BidTooLowException(AuctionEngineException):
    def __init__(self, current_price: Decimal, attempted: Decimal):
        self.current_price = current_price
        self.attempted = attempted
        super().__init__(f"Bid amount {attempted} must be greater than current price {current_price}.")

class AuctionNotActiveException(AuctionEngineException):
    def __init__(self, auction_id: UUID, status: str):
        self.auction_id = auction_id
        self.status = status
        super().__init__(f"Cannot place a bid on auction {auction_id} because its status is {status}.")

class AuctionNotFoundException(AuctionEngineException):
    def __init__(self, auction_id: UUID):
        self.auction_id = auction_id
        super().__init__(f"Auction with ID {auction_id} was not found.")

class ProductNotFoundException(AuctionEngineException):
    def __init__(self, product_id: UUID):
        self.product_id = product_id
        super().__init__(f"Product with ID {product_id} was not found.")

class DuplicateBidException(AuctionEngineException):
    def __init__(self, idempotency_key: str):
        self.idempotency_key = idempotency_key
        super().__init__(f"A bid with idempotency key {idempotency_key} has already been placed.")

class UnauthorizedProductAccessException(AuctionEngineException):
    def __init__(self, user_id: UUID, product_id: UUID):
        self.user_id = user_id
        self.product_id = product_id
        super().__init__(f"User {user_id} is not authorized to modify or delete product {product_id}.")

