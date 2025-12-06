"""
API dependencies and shared utilities.
"""
from typing import Generator, Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.api_key import ApiKey
from app.services.auth_service import AuthService, ApiKeyService


# Security scheme
security = HTTPBearer(auto_error=False)


def get_database() -> Generator:
    """
    Database session dependency.
    """
    return get_db()


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if JWT token is provided, otherwise return None.
    Useful for endpoints that can work with or without authentication.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    
    if not payload or payload.get("type") != "access":
        return None
    
    user_id = int(payload.get("sub"))
    user = AuthService.get_user_by_id(db, user_id)
    
    if user and user.is_active:
        return user
    
    return None


async def get_api_key_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[ApiKey]:
    """
    Get API key if provided, otherwise return None.
    Useful for endpoints that can work with or without API key authentication.
    """
    if not credentials:
        return None
    
    api_key = credentials.credentials
    
    try:
        key_obj = ApiKeyService.verify_api_key(db, api_key)
        return key_obj
    except Exception:
        return None


async def get_auth_context(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get authentication context with information about the authentication type.
    Returns a dict with:
    - auth_type: "user", "service", or "none"
    - user: User object if authenticated with JWT
    - api_key: ApiKey object if authenticated with API key
    """
    if not credentials:
        return {"auth_type": "none", "user": None, "api_key": None}
    
    token_or_key = credentials.credentials
    
    # Try JWT first
    payload = AuthService.verify_token(token_or_key)
    if payload and payload.get("type") == "access":
        user_id = int(payload.get("sub"))
        user = AuthService.get_user_by_id(db, user_id)
        if user and user.is_active:
            return {"auth_type": "user", "user": user, "api_key": None}
    
    # Try API key
    try:
        api_key = ApiKeyService.verify_api_key(db, token_or_key)
        if api_key:
            return {"auth_type": "service", "user": None, "api_key": api_key}
    except Exception:
        pass
    
    return {"auth_type": "none", "user": None, "api_key": None}


def require_auth_type(*allowed_types: str):
    """
    Dependency factory to require specific authentication types.
    
    Usage:
        Depends(require_auth_type("user"))  # Only JWT tokens
        Depends(require_auth_type("service"))  # Only API keys
        Depends(require_auth_type("user", "service"))  # Either JWT or API key
    
    Returns the authentication context.
    """
    async def checker(
        auth_context: dict = Depends(get_auth_context)
    ) -> dict:
        if auth_context["auth_type"] not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication required. Accepted types: {', '.join(allowed_types)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return auth_context
    
    return checker
