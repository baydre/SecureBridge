from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.api_key import (
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyCreated,
    ApiKeyUpdate,
    ApiKeyRenew,
)
from app.services.auth_service import ApiKeyService
from app.middleware.auth_middleware import (
    get_current_active_user,
    verify_api_key_dependency,
)
from app.models.user import User
from app.models.api_key import ApiKey

router = APIRouter(prefix="/keys", tags=["API Keys"])


@router.post("/create", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new API key for service-to-service authentication.
    
    **Important**: The API key is returned only once. Store it securely.
    
    - **service_name**: Name of the service using this key
    - **description**: Optional description of the key's purpose
    - **permissions**: List of permissions/scopes for this key
    - **expires_in_days**: Number of days until expiration (default: 90, max: 365)
    
    Requires user authentication (JWT).
    """
    api_key, plain_key = ApiKeyService.create_api_key(db, key_data, current_user.id)
    
    # Build response with the plain API key (shown only once)
    response = ApiKeyCreated(
        id=api_key.id,
        api_key=plain_key,
        service_name=api_key.service_name,
        description=api_key.description,
        permissions=api_key.permissions,
        is_active=api_key.is_active,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        created_by=api_key.created_by,
    )
    
    return response


@router.get("/list", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List all API keys created by the current user.
    
    Returns all keys with their status, expiration, and permissions.
    Does not include the actual API key values.
    
    Requires user authentication (JWT).
    """
    api_keys = ApiKeyService.get_user_api_keys(db, current_user.id)
    return api_keys


@router.get("/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get details of a specific API key.
    
    - **key_id**: ID of the API key
    
    Requires user authentication (JWT).
    Only the key owner can view the key details.
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.created_by == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return api_key


@router.patch("/{key_id}/revoke", response_model=ApiKeyResponse)
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Revoke (deactivate) an API key.
    
    - **key_id**: ID of the API key to revoke
    
    The key will be marked as inactive and cannot be used for authentication.
    
    Requires user authentication (JWT).
    """
    api_key = ApiKeyService.revoke_api_key(db, key_id, current_user.id)
    return api_key


@router.patch("/{key_id}/renew", response_model=ApiKeyResponse)
async def renew_api_key(
    key_id: int,
    renew_data: ApiKeyRenew,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Renew an API key by extending its expiration date.
    
    - **key_id**: ID of the API key to renew
    - **expires_in_days**: Number of days to extend from now (default: 90, max: 365)
    
    Requires user authentication (JWT).
    """
    api_key = ApiKeyService.renew_api_key(
        db, key_id, current_user.id, renew_data.expires_in_days
    )
    return api_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Permanently delete an API key.
    
    - **key_id**: ID of the API key to delete
    
    This action cannot be undone.
    
    Requires user authentication (JWT).
    """
    ApiKeyService.delete_api_key(db, key_id, current_user.id)
    return None


@router.get("/verify/test", response_model=dict)
async def verify_api_key_test(
    api_key: ApiKey = Depends(verify_api_key_dependency),
):
    """
    Test endpoint to verify API key authentication.
    
    Use this endpoint to test if your API key is valid and active.
    
    Requires API key in Authorization header: Bearer <your-api-key>
    """
    return {
        "message": "API key is valid",
        "service_name": api_key.service_name,
        "permissions": api_key.permissions,
        "expires_at": api_key.expires_at,
    }
