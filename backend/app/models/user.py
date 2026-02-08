"""
User Model - Citizens using the SUVIDHA kiosk
"""
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    SENIOR_CITIZEN = "senior_citizen"
    PWD = "pwd"  # Person with Disability


class User(Base):
    """
    Citizen/Customer model for SUVIDHA
    Personal data is encrypted at rest
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Unique identifiers
    consumer_number = Column(String(50), unique=True, index=True, nullable=True)
    mobile_encrypted = Column(Text, nullable=False)  # AES encrypted
    mobile_hash = Column(String(64), unique=True, index=True, nullable=False)  # SHA256 for lookup
    
    # Optional identifiers (encrypted)
    aadhaar_encrypted = Column(Text, nullable=True)
    aadhaar_hash = Column(String(64), unique=True, index=True, nullable=True)
    
    # Profile
    full_name = Column(String(200), nullable=True)
    email_encrypted = Column(Text, nullable=True)
    address_encrypted = Column(Text, nullable=True)
    
    # Role and preferences
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, nullable=False)
    preferred_language = Column(String(10), default="en", nullable=False)
    accessibility_needs = Column(Text, nullable=True)  # JSON string of preferences
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    bills = relationship("Bill", back_populates="user", lazy="dynamic")
    payments = relationship("Payment", back_populates="user", lazy="dynamic")
    grievances = relationship("Grievance", back_populates="user", lazy="dynamic")
    connection_requests = relationship("ConnectionRequest", back_populates="user", lazy="dynamic")
    documents = relationship("Document", back_populates="user", lazy="dynamic")
    
    def __repr__(self):
        return f"<User(id={self.id}, consumer={self.consumer_number})>"
