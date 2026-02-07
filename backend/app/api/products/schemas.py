from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class ProductResponse(BaseModel):
    product_uuid: UUID
    name: str
    sku: str
    description: Optional[str]
    price: float
    image_url: Optional[str]
    stock: int
    category: Optional[str]
    qr_code_data: Optional[str]
    is_active: int
    
    class Config:
        from_attributes = True

class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    stock: int = Field(default=0, ge=0)
    category: Optional[str] = None

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    is_active: Optional[int] = Field(None, ge=0, le=1)

class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int
    page: int
    limit: int
