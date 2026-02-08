"""
Admin Model - Staff and administrators
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class Admin(Base):
    """
    Admin/Staff model for SUVIDHA backend management
    """
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Credentials
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    
    # Profile
    full_name = Column(String(200), nullable=False)
    department = Column(String(100), nullable=True)  # Electricity, Gas, Water, Municipal
    
    # Role and permissions
    role = Column(Enum(AdminRole), default=AdminRole.VIEWER, nullable=False)
    permissions = Column(Text, nullable=True)  # JSON string of specific permissions
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Admin(id={self.id}, username={self.username}, role={self.role})>"
