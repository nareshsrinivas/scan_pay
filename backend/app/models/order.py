from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Order(Base):
    __tablename__ = "orders"
    
    order_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.user_uuid"), nullable=False, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, paid, verified, expired, failed
    items_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")
    exit_qr = relationship("ExitQR", back_populates="order", uselist=False, cascade="all, delete-orphan")
