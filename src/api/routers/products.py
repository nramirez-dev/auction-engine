from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.schemas.product import CreateProductRequest, ProductResponse, DeleteProductRequest
from src.api.deps import (
    get_create_product_use_case,
    get_list_products_use_case,
    get_get_product_use_case,
    get_delete_product_use_case,
)
from src.application.products import (
    CreateProductUseCase,
    ListProductsUseCase,
    GetProductUseCase,
    DeleteProductUseCase,
)

router = APIRouter(prefix="/products", tags=["products"])

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: CreateProductRequest,
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),
):
    product = await use_case.execute(
        owner_id=request.owner_id,
        title=request.title,
        description=request.description,
        starting_price=request.starting_price,
    )
    return product

@router.get("", response_model=List[ProductResponse], status_code=status.HTTP_200_OK)
async def list_products(
    use_case: ListProductsUseCase = Depends(get_list_products_use_case),
):
    products = await use_case.execute()
    return products

@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(
    product_id: UUID,
    use_case: GetProductUseCase = Depends(get_get_product_use_case),
):
    """
    Retrieves a specific product by ID.
    """
    product = await use_case.execute(product_id)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    request: DeleteProductRequest,
    use_case: DeleteProductUseCase = Depends(get_delete_product_use_case),
):
    """
    Deletes a product as long as the requester is authorized.
    """
    await use_case.execute(product_id=product_id, requester_id=request.requester_id)
