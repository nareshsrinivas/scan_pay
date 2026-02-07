from sqlalchemy.orm import Session
from app.models.staff import Staff
from app.core.security import hash_password, verify_password, create_access_token
from app.api.staff.schemas import StaffLoginRequest, StaffCreateRequest
from fastapi import HTTPException, status
from datetime import datetime

class StaffService:
    
    @staticmethod
    def login(db: Session, request: StaffLoginRequest):
        """Staff login"""
        
        staff = db.query(Staff).filter(Staff.email == request.email).first()
        
        if not staff or not verify_password(request.password, staff.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not staff.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff account is inactive"
            )
        
        # Update last login
        staff.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(staff.staff_uuid),
                "role": "staff",
                "type": "staff"
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "staff_uuid": staff.staff_uuid,
            "email": staff.email,
            "name": staff.name,
            "role": staff.role
        }
    
    @staticmethod
    def create_staff(db: Session, request: StaffCreateRequest):
        """Create new staff member"""
        
        # Check if email exists
        existing = db.query(Staff).filter(Staff.email == request.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = hash_password(request.password)
        
        staff = Staff(
            email=request.email,
            password_hash=password_hash,
            name=request.name,
            role=request.role
        )
        
        db.add(staff)
        db.commit()
        db.refresh(staff)
        
        return {
            "staff_uuid": staff.staff_uuid,
            "email": staff.email,
            "name": staff.name,
            "role": staff.role,
            "is_active": staff.is_active,
            "created_at": staff.created_at.isoformat()
        }
