from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import create_access_token
from app.api.auth.schemas import GuestLoginRequest, GuestLoginResponse
from datetime import timedelta

class AuthService:
    
    @staticmethod
    def guest_login(db: Session, request: GuestLoginRequest) -> GuestLoginResponse:
        """Handle guest login - create user if not exists"""
        
        # Check if user exists
        user = db.query(User).filter(User.phone_number == request.phone_number).first()
        
        if not user:
            # Create new user
            user = User(
                phone_number=request.phone_number,
                device_id=request.device_id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update device_id if changed
            if request.device_id and user.device_id != request.device_id:
                user.device_id = request.device_id
                db.commit()
                db.refresh(user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.user_uuid), "type": "user"}
        )
        
        return GuestLoginResponse(
            access_token=access_token,
            user_uuid=user.user_uuid,
            phone_number=user.phone_number
        )
    
    @staticmethod
    def get_user_profile(user: User):
        """Get user profile"""
        return {
            "user_uuid": user.user_uuid,
            "phone_number": user.phone_number,
            "name": user.name,
            "created_at": user.created_at.isoformat()
        }
