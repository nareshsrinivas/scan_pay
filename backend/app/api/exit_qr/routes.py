from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.exit_qr.schemas import (
    ExitQRGenerateRequest,
    ExitQRResponse,
    ExitQRVerifyRequest,
    ExitQRVerifyResponse
)
from app.api.exit_qr.service import ExitQRService
from app.core.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.config import settings
from typing import Optional

router = APIRouter(prefix="/exit-qr", tags=["Exit QR"])

@router.post("/generate", response_model=ExitQRResponse)
async def generate_exit_qr(
    request: ExitQRGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate exit QR code after successful payment
    """
    return ExitQRService.generate_exit_qr(db, request)

@router.post("/verify", response_model=ExitQRVerifyResponse)
async def verify_exit_qr(
    request: ExitQRVerifyRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Verify exit QR code at gate (can be used by staff without auth or with auth)
    """
    staff_id = str(current_user.user_uuid) if current_user else "gate_scanner"
    return ExitQRService.verify_exit_qr(db, request, staff_id)


# Internal endpoint for n8n workflow (no user auth required)
@router.post("/internal/generate", response_model=ExitQRResponse)
async def internal_generate_exit_qr(
    request: ExitQRGenerateRequest,
    x_internal_secret: str = Header(..., alias="X-Internal-Secret"),
    db: Session = Depends(get_db)
):
    """
    Internal endpoint for n8n workflow to generate exit QR.
    Requires X-Internal-Secret header for authentication.
    """
    # Verify internal secret
    expected_secret = getattr(settings, 'INTERNAL_API_SECRET', 'n8n-internal-secret-key')
    if x_internal_secret != expected_secret:
        raise HTTPException(status_code=401, detail="Invalid internal secret")
    
    return ExitQRService.generate_exit_qr(db, request)

