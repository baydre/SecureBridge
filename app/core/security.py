from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from cryptography.fernet import Fernet
import secrets
import base64
from app.core.config import settings


# Password hashing using bcrypt directly
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Bcrypt has a 72 byte limit, truncate password if needed
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')


# JWT Token operations
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# API Key operations
class APIKeyManager:
    """Manager for API key encryption and generation."""
    
    def __init__(self):
        # Generate a Fernet key from the encryption key
        encryption_key = settings.API_KEY_ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
        key = base64.urlsafe_b64encode(encryption_key)
        self.cipher = Fernet(key)
    
    def generate_api_key(self) -> str:
        """Generate a secure random API key."""
        random_string = secrets.token_urlsafe(32)
        return f"{settings.API_KEY_PREFIX}{random_string}"
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt an API key for storage."""
        encrypted = self.cipher.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt an API key from storage."""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            return ""


api_key_manager = APIKeyManager()


# Expose API key functions
def generate_api_key() -> str:
    """Generate a secure random API key."""
    return api_key_manager.generate_api_key()


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage."""
    return api_key_manager.encrypt_api_key(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from storage."""
    return api_key_manager.decrypt_api_key(encrypted_key)
