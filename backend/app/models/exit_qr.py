from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class ExitQR(Base):
    __tablename__ = "exit_qrs"
    
    exit_qr_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_uuid = Column(UUID(as_uuid=True), ForeignKey("orders.order_uuid"), nullable=False, unique=True, index=True)
    token = Column(Text, nullable=False, unique=True, index=True)
    qr_image_path = Column(String(500), nullable=True)
    used = Column(Boolean, default=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True)
    verified_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="exit_qr")
