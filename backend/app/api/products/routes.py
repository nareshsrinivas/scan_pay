from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.products.schemas import (
    ProductResponse,
    ProductListResponse,
    ProductCreateRequest,
    ProductUpdateRequest
)
from app.api.products.service import ProductService
from typing import Optional
from uuid import UUID

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get all products with pagination and optional filters
    """
    return ProductService.get_all_products(db, page, limit, search, category)

@router.get("/{product_uuid}", response_model=ProductResponse)
async def get_product(
    product_uuid: UUID,
    db: Session = Depends(get_db)
):
    """
    Get product by UUID
    """
    return ProductService.get_product_by_uuid(db, product_uuid)

@router.get("/qr/{qr_code_data}", response_model=ProductResponse)
async def get_product_by_qr(
    qr_code_data: str,
    db: Session = Depends(get_db)
):
    """
    Get product by QR code data (for scanning)
    """
    return ProductService.get_product_by_qr(db, qr_code_data)

@router.post("", response_model=ProductResponse)
async def create_product(
    request: ProductCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create new product (Admin only in production)
    """
    return ProductService.create_product(db, request)

@router.put("/{product_uuid}", response_model=ProductResponse)
async def update_product(
    product_uuid: UUID,
    request: ProductUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update product (Admin only in production)
    """
    return ProductService.update_product(db, product_uuid, request)

@router.delete("/{product_uuid}")
async def delete_product(
    product_uuid: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete product (Admin only in production)
    """
    return ProductService.delete_product(db, product_uuid)
