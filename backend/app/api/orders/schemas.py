from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime

class OrderItemResponse(BaseModel):
    order_item_uuid: UUID
    product_uuid: UUID
    product_name: str
    product_sku: str
    price: float
    quantity: int
    subtotal: float
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    order_uuid: UUID
    order_number: str
    user_uuid: UUID
    subtotal: float
    tax_amount: float
    total_amount: float
    status: str
    items_count: int
    created_at: str
    expires_at: Optional[str]
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

class OrderCreateResponse(BaseModel):
    order_uuid: UUID
    order_number: str
    total_amount: float
    status: str
    message: str
