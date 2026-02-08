"""
Connection Request Model - New utility connections
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class ConnectionType(str, enum.Enum):
    ELECTRICITY_DOMESTIC = "electricity_domestic"
    ELECTRICITY_COMMERCIAL = "electricity_commercial"
    ELECTRICITY_INDUSTRIAL = "electricity_industrial"
    GAS_DOMESTIC = "gas_domestic"
    GAS_COMMERCIAL = "gas_commercial"
    WATER_DOMESTIC = "water_domestic"
    WATER_COMMERCIAL = "water_commercial"
    SEWERAGE = "sewerage"


class ConnectionStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    DOCUMENTS_PENDING = "documents_pending"
    DOCUMENTS_VERIFIED = "documents_verified"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_RECEIVED = "payment_received"
    SITE_INSPECTION_PENDING = "site_inspection_pending"
    SITE_INSPECTION_DONE = "site_inspection_done"
    APPROVED = "approved"
    WORK_IN_PROGRESS = "work_in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ConnectionRequest(Base):
    """
    New connection request model with workflow tracking
    """
    __tablename__ = "connection_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Application tracking
    application_number = Column(String(20), unique=True, index=True, nullable=False)  # e.g., CON2024010001
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Connection details
    connection_type = Column(Enum(ConnectionType), nullable=False)
    load_requirement = Column(String(50), nullable=True)  # e.g., "5 KW" for electricity
    purpose = Column(String(200), nullable=True)
    
    # Applicant details (can differ from user)
    applicant_name = Column(String(200), nullable=False)
    applicant_mobile = Column(String(20), nullable=False)
    applicant_email = Column(String(200), nullable=True)
    
    # Property details
    property_type = Column(String(50), nullable=True)  # Owned, Rented
    property_address = Column(Text, nullable=False)
    property_landmark = Column(String(200), nullable=True)
    property_pin = Column(String(10), nullable=False)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # Status
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.DRAFT, nullable=False)
    current_step = Column(Integer, default=1, nullable=False)
    total_steps = Column(Integer, default=5, nullable=False)
    
    # Fees
    application_fee = Column(Numeric(12, 2), nullable=True)
    connection_fee = Column(Numeric(12, 2), nullable=True)
    security_deposit = Column(Numeric(12, 2), nullable=True)
    total_fee = Column(Numeric(12, 2), nullable=True)
    fee_paid = Column(Boolean, default=False, nullable=False)
    
    # Inspection
    inspection_date = Column(DateTime, nullable=True)
    inspection_officer = Column(String(200), nullable=True)
    inspection_notes = Column(Text, nullable=True)
    inspection_passed = Column(Boolean, nullable=True)
    
    # Final details
    assigned_consumer_number = Column(String(50), nullable=True)
    meter_number = Column(String(50), nullable=True)
    connection_date = Column(DateTime, nullable=True)
    
    # Rejection
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="connection_requests")
    documents = relationship("Document", back_populates="connection_request", lazy="dynamic")
    
    def __repr__(self):
        return f"<ConnectionRequest(id={self.id}, app={self.application_number}, type={self.connection_type})>"
