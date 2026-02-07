from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class ExitQRGenerateRequest(BaseModel):
    order_uuid: UUID

class ExitQRResponse(BaseModel):
    exit_qr_uuid: UUID
    order_uuid: UUID
    token: str
    qr_image: str  # Base64 encoded image
    expires_at: str
    order_number: str
    total_amount: float
    message: str

class ExitQRVerifyRequest(BaseModel):
    qr_token: str

class ExitQRVerifyResponse(BaseModel):
    valid: bool
    order_uuid: Optional[UUID]
    order_number: Optional[str]
    user_name: Optional[str]
    total_amount: Optional[float]
    items_count: Optional[int]
    items: Optional[list]
    message: str
    status: str  # authorized, expired, already_used, invalid
