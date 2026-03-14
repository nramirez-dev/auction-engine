from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

@dataclass
class Bid:
    id: UUID
    auction_id: UUID
    user_id: UUID
    amount: Decimal
    placed_at: datetime
    idempotency_key: Optional[str] = None
