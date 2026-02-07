from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class CartAddRequest(BaseModel):
    product_uuid: UUID
    quantity: int = Field(..., ge=1)

class CartItemResponse(BaseModel):
    cart_uuid: UUID
    product_uuid: UUID
    product_name: str
    product_sku: str
    product_price: float
    product_image: Optional[str]
    quantity: int
    subtotal: float
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_items: int
    subtotal: float
    tax_amount: float
    total_amount: float

class CartUpdateRequest(BaseModel):
    quantity: int = Field(..., ge=0)
