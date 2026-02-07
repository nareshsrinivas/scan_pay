from fastapi import APIRouter, Depends
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
