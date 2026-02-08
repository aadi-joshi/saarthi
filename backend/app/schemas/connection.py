"""
Connection Request Pydantic Schemas
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum
import re


class ConnectionType(str, Enum):
    ELECTRICITY_DOMESTIC = "electricity_domestic"
    ELECTRICITY_COMMERCIAL = "electricity_commercial"
    ELECTRICITY_INDUSTRIAL = "electricity_industrial"
    GAS_DOMESTIC = "gas_domestic"
    GAS_COMMERCIAL = "gas_commercial"
    WATER_DOMESTIC = "water_domestic"
    WATER_COMMERCIAL = "water_commercial"
    SEWERAGE = "sewerage"


class ConnectionStatus(str, Enum):
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


class ConnectionCreate(BaseModel):
    """Create new connection request"""
    connection_type: ConnectionType
    load_requirement: Optional[str] = None
    purpose: Optional[str] = None
    
    # Applicant details
    applicant_name: str = Field(..., min_length=3, max_length=200)
    applicant_mobile: str = Field(..., min_length=10, max_length=10)
    applicant_email: Optional[EmailStr] = None
    
    # Property details
    property_type: Optional[str] = None
    property_address: str = Field(..., min_length=10, max_length=500)
    property_landmark: Optional[str] = None
    property_pin: str = Field(..., pattern="^[1-9][0-9]{5}$")
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    
    @field_validator('applicant_mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not re.match(r'^[6-9]\d{9}$', v):
            raise ValueError('Invalid Indian mobile number')
        return v


class ConnectionUpdate(BaseModel):
    """Update connection request"""
    load_requirement: Optional[str] = None
    purpose: Optional[str] = None
    property_address: Optional[str] = None
    property_landmark: Optional[str] = None


class ConnectionResponse(BaseModel):
    """Connection request details"""
    id: int
    application_number: str
    connection_type: ConnectionType
    load_requirement: Optional[str]
    applicant_name: str
    property_address: str
    property_pin: str
    status: ConnectionStatus
    current_step: int
    total_steps: int
    application_fee: Optional[Decimal]
    connection_fee: Optional[Decimal]
    security_deposit: Optional[Decimal]
    total_fee: Optional[Decimal]
    fee_paid: bool
    assigned_consumer_number: Optional[str]
    meter_number: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConnectionListResponse(BaseModel):
    """List of connection requests"""
    connections: List[ConnectionResponse]
    total: int
    pending_count: int
    completed_count: int
