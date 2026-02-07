from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.staff.schemas import (
    StaffLoginRequest,
    StaffLoginResponse,
    StaffCreateRequest,
    StaffResponse
)
from app.api.staff.service import StaffService

router = APIRouter(prefix="/staff", tags=["Staff"])

@router.post("/login", response_model=StaffLoginResponse)
async def staff_login(
    request: StaffLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Staff login endpoint
    """
    return StaffService.login(db, request)

@router.post("/register", response_model=StaffResponse)
async def create_staff(
    request: StaffCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create new staff member (should be admin-only in production)
    """
    return StaffService.create_staff(db, request)
