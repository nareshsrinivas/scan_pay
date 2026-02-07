from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class PaymentInitiateRequest(BaseModel):
    order_uuid: UUID
    payment_method: str = "upi"  # upi, card, netbanking, wallet
    simulate_failure: bool = False  # For demo mode testing

class PaymentInitiateResponse(BaseModel):
    payment_uuid: str
    order_uuid: str
    amount: float
    currency: str = "INR"
    payment_method: str
    payment_url: Optional[str] = None
    qr_code: Optional[str] = None
    provider: str  # "demo" or "razorpay"
    provider_payment_id: Optional[str] = None
    razorpay_key_id: Optional[str] = None  # For Razorpay frontend SDK
    expires_at: Optional[datetime] = None
    status: str = "pending"

class PaymentWebhookRequest(BaseModel):
    order_uuid: Optional[str] = None
    payment_uuid: Optional[str] = None
    status: str
    provider_reference: Optional[str] = None
    transaction_id: Optional[str] = None
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    signature: Optional[str] = None

class PaymentStatusResponse(BaseModel):
    payment_uuid: str
    order_uuid: str
    amount: float
    status: str
    payment_method: Optional[str] = None
    provider: Optional[str] = None
    provider_payment_id: Optional[str] = None
    provider_reference: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
