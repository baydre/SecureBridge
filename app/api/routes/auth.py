from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.auth import Token, AuthResponse, RefreshTokenRequest
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **name**: User's full name
    - **password**: Password (minimum 8 characters)
    
    Returns the created user and authentication tokens.
    """
    # Create user
    user = AuthService.create_user(db, user_data)
    
    # Generate tokens
    tokens = AuthService.generate_tokens(user)
    
    # Prepare response
    user_dict = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
    
    return {
        "user": user_dict,
        "tokens": tokens,
    }


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and generate JWT tokens.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns authentication tokens on successful login.
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens
    tokens = AuthService.generate_tokens(user)
    
    # Prepare response
    user_dict = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
    
    return {
        "user": user_dict,
        "tokens": tokens,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using a refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access and refresh tokens.
    """
    # Verify refresh token
    payload = AuthService.verify_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user_id = int(payload.get("sub"))
    user = AuthService.get_user_by_id(db, user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate new tokens
    tokens = AuthService.generate_tokens(user)
    
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user's information.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
):
    """
    Logout current user.
    
    Note: With JWT, logout is typically handled client-side by removing the token.
    This endpoint is provided for logging purposes or future token blacklist implementation.
    """
    return {"message": "Successfully logged out"}
