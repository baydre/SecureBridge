from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ApiKeyBase(BaseModel):
    """Base API key schema."""
    service_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    permissions: List[str] = Field(default_factory=list)


class ApiKeyCreate(ApiKeyBase):
    """Schema for creating an API key."""
    expires_in_days: Optional[int] = Field(90, ge=1, le=365)


class ApiKeyUpdate(BaseModel):
    """Schema for updating an API key."""
    service_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ApiKeyResponse(BaseModel):
    """Schema for API key response (without the actual key)."""
    id: int
    service_name: str
    description: Optional[str]
    permissions: List[str]
    is_active: bool
    expires_at: datetime
    created_at: datetime
    last_used_at: Optional[datetime]
    created_by: int
    
    class Config:
        from_attributes = True


class ApiKeyCreated(ApiKeyResponse):
    """Schema for newly created API key (includes the actual key - shown only once)."""
    api_key: str
    
    class Config:
        from_attributes = True


class ApiKeyRenew(BaseModel):
    """Schema for renewing an API key."""
    expires_in_days: int = Field(90, ge=1, le=365)
