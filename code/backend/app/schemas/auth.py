from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Request schemas
class UserSignupRequest(BaseModel):
    """Request schema for email/password signup"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    """Request schema for email/password login"""
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """Request schema for Google OAuth"""
    code: str = Field(..., description="Authorization code from Google")


# Response schemas
class TokenResponse(BaseModel):
    """Response schema for authentication (login/signup)"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """User data returned in responses"""
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class GoogleAuthURLResponse(BaseModel):
    """Response with Google OAuth authorization URL"""
    authorization_url: str
