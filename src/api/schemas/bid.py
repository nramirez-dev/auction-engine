from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

class PlaceBidRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    auction_id: UUID
    user_id: UUID
    amount: Decimal = Field(gt=0)

class PlaceBidResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    auction_id: UUID
    user_id: UUID
    amount: Decimal
    placed_at: datetime
