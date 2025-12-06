from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class AuthResponse(BaseModel):
    """Schema for authentication response."""
    user: dict
    tokens: Token


class ActivityLog(BaseModel):
    """Schema for authentication activity logs."""
    timestamp: datetime
    action: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: bool
    
    class Config:
        from_attributes = True
