from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID

class GuestLoginRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15)
    device_id: Optional[str] = None
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if not v.isdigit():
            raise ValueError('Phone number must contain only digits')
        return v

class GuestLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_uuid: UUID
    phone_number: str
    
    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    user_uuid: UUID
    phone_number: str
    name: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True
