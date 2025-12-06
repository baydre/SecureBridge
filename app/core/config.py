from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SecureBridge"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    API_VERSION: str = "v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    API_KEY_ENCRYPTION_KEY: str
    
    # API Key Settings
    API_KEY_DEFAULT_EXPIRATION_DAYS: int = 90
    API_KEY_PREFIX: str = "sbk_"
    
    # Database
    DATABASE_URL: str = "sqlite:///./securebridge.db"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Admin User
    ADMIN_EMAIL: str = "admin@securebridge.com"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()