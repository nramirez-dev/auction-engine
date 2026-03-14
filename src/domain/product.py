from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

@dataclass
class Product:
    id: UUID
    owner_id: UUID
    title: str
    starting_price: Decimal
    created_at: datetime
    description: Optional[str] = None
