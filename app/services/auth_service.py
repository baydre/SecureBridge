from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.api_key import ApiKey
from app.schemas.user import UserCreate
from app.schemas.api_key import ApiKeyCreate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
    encrypt_api_key,
    decrypt_api_key,
)
from app.core.config import settings


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user with hashed password.
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_pwd = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_pwd,
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def generate_tokens(user: User) -> dict:
        """
        Generate access and refresh tokens for a user.
        """
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token.
        """
        return decode_token(token)
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get a user by their ID.
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get a user by their email.
        """
        return db.query(User).filter(User.email == email).first()


class ApiKeyService:
    """Service for handling API key operations."""
    
    @staticmethod
    def create_api_key(db: Session, key_data: ApiKeyCreate, user_id: int) -> tuple[ApiKey, str]:
        """
        Create a new API key for a user.
        Returns the ApiKey model and the plain text API key (shown only once).
        """
        # Generate API key
        plain_key = generate_api_key()
        encrypted_key = encrypt_api_key(plain_key)
        
        # Calculate expiration date
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days or 90)
        
        # Create API key record
        api_key = ApiKey(
            key_hash=encrypted_key,
            service_name=key_data.service_name,
            description=key_data.description,
            permissions=key_data.permissions,
            expires_at=expires_at,
            created_by=user_id,
        )
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        
        return api_key, plain_key
    
    @staticmethod
    def verify_api_key(db: Session, plain_key: str) -> Optional[ApiKey]:
        """
        Verify an API key and return the associated ApiKey object.
        """
        # Get all active API keys
        api_keys = db.query(ApiKey).filter(ApiKey.is_active == True).all()
        
        # Try to match the plain key with encrypted keys
        for api_key in api_keys:
            try:
                decrypted = decrypt_api_key(api_key.key_hash)
                if decrypted == plain_key:
                    # Check if key is expired
                    if api_key.expires_at < datetime.utcnow():
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="API key has expired"
                        )
                    
                    # Update last used timestamp
                    api_key.last_used_at = datetime.utcnow()
                    db.commit()
                    
                    return api_key
            except Exception:
                continue
        
        return None
    
    @staticmethod
    def get_user_api_keys(db: Session, user_id: int) -> list[ApiKey]:
        """
        Get all API keys created by a user.
        """
        return db.query(ApiKey).filter(ApiKey.created_by == user_id).all()
    
    @staticmethod
    def revoke_api_key(db: Session, key_id: int, user_id: int) -> ApiKey:
        """
        Revoke (deactivate) an API key.
        """
        api_key = db.query(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.created_by == user_id
        ).first()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        api_key.is_active = False
        db.commit()
        db.refresh(api_key)
        
        return api_key
    
    @staticmethod
    def renew_api_key(db: Session, key_id: int, user_id: int, expires_in_days: int) -> ApiKey:
        """
        Renew an API key by extending its expiration date.
        """
        api_key = db.query(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.created_by == user_id
        ).first()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        # Extend expiration
        api_key.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        api_key.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(api_key)
        
        return api_key
    
    @staticmethod
    def delete_api_key(db: Session, key_id: int, user_id: int) -> None:
        """
        Permanently delete an API key.
        """
        api_key = db.query(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.created_by == user_id
        ).first()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        db.delete(api_key)
        db.commit()
