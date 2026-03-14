import enum
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

class AuctionStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"

@dataclass
class Auction:
    id: UUID
    product_id: UUID
    status: AuctionStatus
    current_price: Decimal
    started_at: datetime
    winner_id: Optional[UUID] = None
    closed_at: Optional[datetime] = None
