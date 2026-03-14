from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

class CreateProductRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    owner_id: UUID
    title: str
    description: Optional[str] = None
    starting_price: Decimal = Field(gt=0)

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    owner_id: UUID
    title: str
    description: Optional[str]
    starting_price: Decimal
    created_at: datetime

class DeleteProductRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    requester_id: UUID
