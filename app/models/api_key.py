from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class ApiKey(Base):
    """API Key model for service-to-service authentication."""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String, unique=True, index=True, nullable=False)  # Encrypted API key
    service_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    permissions = Column(JSON, default=list)  # List of allowed permissions/scopes
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # Foreign key to User
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship
    owner = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<ApiKey {self.service_name}>"
