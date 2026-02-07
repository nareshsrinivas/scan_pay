from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    payment_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_uuid = Column(UUID(as_uuid=True), ForeignKey("orders.order_uuid"), nullable=False, unique=True, index=True)
    transaction_id = Column(String(255), nullable=True, index=True)
    upi_txn_id = Column(String(255), nullable=True)
    payment_provider = Column(String(50), nullable=False)  # razorpay, phonepe, paytm, etc
    payment_method = Column(String(50), nullable=True)  # upi, card, netbanking
    amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, success, failed
    gateway_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="payment")
