from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product
from app.api.products.schemas import ProductCreateRequest, ProductUpdateRequest
from fastapi import HTTPException, status
from uuid import UUID
from typing import Optional

class ProductService:
    
    @staticmethod
    def get_all_products(
        db: Session,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None
    ):
        """Get all active products with pagination and filters"""
        
        query = db.query(Product).filter(Product.is_active == 1)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        if category:
            query = query.filter(Product.category == category)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        products = query.offset(offset).limit(limit).all()
        
        return {
            "products": products,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    @staticmethod
    def get_product_by_uuid(db: Session, product_uuid: UUID):
        """Get product by UUID"""
        product = db.query(Product).filter(
            Product.product_uuid == product_uuid,
            Product.is_active == 1
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return product
    
    @staticmethod
    def get_product_by_qr(db: Session, qr_code_data: str):
        """Get product by QR code data"""
        product = db.query(Product).filter(
            Product.qr_code_data == qr_code_data,
            Product.is_active == 1
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found for this QR code"
            )
        
        return product
    
    @staticmethod
    def create_product(db: Session, request: ProductCreateRequest):
        """Create new product"""
        
        # Check if SKU already exists
        existing = db.query(Product).filter(Product.sku == request.sku).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
        
        # Generate QR code data using SKU for consistency with seed data
        qr_code_data = f"PRODUCT:{request.sku}"
        
        product = Product(
            **request.dict(),
            qr_code_data=qr_code_data
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def update_product(db: Session, product_uuid: UUID, request: ProductUpdateRequest):
        """Update product"""
        product = db.query(Product).filter(Product.product_uuid == product_uuid).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Update fields
        for field, value in request.dict(exclude_unset=True).items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def delete_product(db: Session, product_uuid: UUID):
        """Soft delete product"""
        product = db.query(Product).filter(Product.product_uuid == product_uuid).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product.is_active = 0
        db.commit()
        
        return {"message": "Product deleted successfully"}
