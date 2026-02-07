from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Cart(Base):
    __tablename__ = "carts"
    
    cart_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.user_uuid"), nullable=False, index=True)
    product_uuid = Column(UUID(as_uuid=True), ForeignKey("products.product_uuid"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="cart_items")
