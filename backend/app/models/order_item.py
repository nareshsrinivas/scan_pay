from sqlalchemy import Column, Float, Integer, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    
    order_item_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_uuid = Column(UUID(as_uuid=True), ForeignKey("orders.order_uuid"), nullable=False, index=True)
    product_uuid = Column(UUID(as_uuid=True), ForeignKey("products.product_uuid"), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    subtotal = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
