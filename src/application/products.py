import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from src.domain.product import Product
from src.domain.interfaces import IProductRepository
from src.domain.exceptions import ProductNotFoundException, UnauthorizedProductAccessException

class CreateProductUseCase:
    """Use case for creating a new product."""

    def __init__(self, product_repo: IProductRepository):
        self._product_repo = product_repo
        
    async def execute(self, owner_id: uuid.UUID, title: str, description: Optional[str], starting_price: Decimal) -> Product:
        product = Product(
            id=uuid.uuid4(),
            owner_id=owner_id,
            title=title,
            description=description,
            starting_price=starting_price,
            created_at=datetime.now(timezone.utc)
        )
        return await self._product_repo.save(product)

class GetProductUseCase:
    """Use case for retrieving a single product by its ID."""

    def __init__(self, product_repo: IProductRepository):
        self._product_repo = product_repo
        
    async def execute(self, product_id: uuid.UUID) -> Product:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
        return product

class DeleteProductUseCase:
    """Use case for deleting a product, ensuring the requester is the owner."""

    def __init__(self, product_repo: IProductRepository):
        self._product_repo = product_repo
        
    async def execute(self, product_id: uuid.UUID, requester_id: uuid.UUID) -> None:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
            
        if product.owner_id != requester_id:
            raise UnauthorizedProductAccessException(requester_id, product_id)
            
        await self._product_repo.delete(product_id)

class ListProductsUseCase:
    """Use case for listing all available products."""

    def __init__(self, product_repo: IProductRepository):
        self._product_repo = product_repo
        
    async def execute(self) -> list[Product]:
        return await self._product_repo.get_all()

