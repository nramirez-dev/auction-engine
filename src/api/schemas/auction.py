import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from src.domain.auction import AuctionStatus

class CreateAuctionRequest(BaseModel):
    product_id: uuid.UUID = Field(..., description="The ID of the product to auction")
    owner_id: uuid.UUID = Field(..., description="The ID of the product owner")

class AuctionResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    status: AuctionStatus
    current_price: Decimal
    winner_id: Optional[uuid.UUID] = None
    started_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
