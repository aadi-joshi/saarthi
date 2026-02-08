"""
User Pydantic Schemas
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re


class UserRole(str, Enum):
    CITIZEN = "citizen"
    SENIOR_CITIZEN = "senior_citizen"
    PWD = "pwd"


class UserLogin(BaseModel):
    """Login request with mobile number"""
    mobile: str = Field(..., min_length=10, max_length=10, description="10-digit mobile number")
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not re.match(r'^[6-9]\d{9}$', v):
            raise ValueError('Invalid Indian mobile number')
        return v


class OTPVerify(BaseModel):
    """OTP verification request"""
    mobile: str = Field(..., min_length=10, max_length=10)
    otp: str = Field(..., min_length=6, max_length=6)
    
    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        return v


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user_id: int
    is_new_user: bool = False


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class UserCreate(BaseModel):
    """User registration/profile update"""
    mobile: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    aadhaar: Optional[str] = Field(None, min_length=12, max_length=12)
    address: Optional[str] = None
    consumer_number: Optional[str] = None
    role: UserRole = UserRole.CITIZEN
    preferred_language: str = Field("en", pattern="^(en|hi)$")
    accessibility_needs: Optional[dict] = None
    
    @field_validator('aadhaar')
    @classmethod
    def validate_aadhaar(cls, v):
        if v and not re.match(r'^\d{12}$', v):
            raise ValueError('Invalid Aadhaar number')
        return v


class UserUpdate(BaseModel):
    """User profile update"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    consumer_number: Optional[str] = None
    preferred_language: Optional[str] = Field(None, pattern="^(en|hi)$")
    accessibility_needs: Optional[dict] = None


class UserResponse(BaseModel):
    """User data response (without sensitive fields)"""
    id: int
    consumer_number: Optional[str]
    full_name: Optional[str]
    mobile_masked: str  # "******1234"
    role: UserRole
    preferred_language: str
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True
