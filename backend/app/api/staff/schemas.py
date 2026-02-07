from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional

class StaffLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class StaffLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    staff_uuid: UUID
    email: str
    name: str
    role: str
    
    class Config:
        from_attributes = True

class StaffCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="staff")

class StaffResponse(BaseModel):
    staff_uuid: UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True
