from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.auth.schemas import GuestLoginRequest, GuestLoginResponse, UserProfileResponse
from app.api.auth.service import AuthService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/guest-login", response_model=GuestLoginResponse)
async def guest_login(
    request: GuestLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Guest login endpoint - creates user if not exists, returns JWT token
    """
    try:
        return AuthService.guest_login(db, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile
    """
    return AuthService.get_user_profile(current_user)

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint (token invalidation handled on client side)
    """
    return {
        "success": True,
        "message": "Logged out successfully"
    }
