"""
Grievance Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GrievanceCategory(str, Enum):
    BILLING_DISPUTE = "billing_dispute"
    METER_ISSUE = "meter_issue"
    POWER_OUTAGE = "power_outage"
    GAS_LEAK = "gas_leak"
    WATER_SUPPLY = "water_supply"
    SEWERAGE = "sewerage"
    STREET_LIGHT = "street_light"
    GARBAGE_COLLECTION = "garbage_collection"
    ROAD_MAINTENANCE = "road_maintenance"
    PROPERTY_TAX = "property_tax"
    STAFF_BEHAVIOUR = "staff_behaviour"
    SERVICE_DELAY = "service_delay"
    OTHER = "other"


class GrievanceStatus(str, Enum):
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class GrievanceCreate(BaseModel):
    """Create new grievance"""
    category: GrievanceCategory
    sub_category: Optional[str] = None
    subject: str = Field(..., min_length=10, max_length=300)
    description: str = Field(..., min_length=20, max_length=2000)
    location_address: Optional[str] = None
    location_landmark: Optional[str] = None
    location_pin: Optional[str] = Field(None, pattern="^[1-9][0-9]{5}$")
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    related_account: Optional[str] = None
    related_bill_id: Optional[int] = None


class GrievanceUpdate(BaseModel):
    """Update grievance (by citizen)"""
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    location_address: Optional[str] = None
    feedback: Optional[int] = Field(None, ge=1, le=5)
    feedback_comment: Optional[str] = None


class GrievanceResponse(BaseModel):
    """Grievance details response"""
    id: int
    tracking_id: str
    category: GrievanceCategory
    sub_category: Optional[str]
    subject: str
    description: str
    location_address: Optional[str]
    status: GrievanceStatus
    priority: int
    assigned_department: Optional[str]
    expected_resolution_date: Optional[datetime]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    acknowledged_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class GrievanceListResponse(BaseModel):
    """List of grievances"""
    grievances: List[GrievanceResponse]
    total: int
    pending_count: int
    resolved_count: int


class GrievanceTrack(BaseModel):
    """Grievance tracking response"""
    tracking_id: str
    status: GrievanceStatus
    status_description: str
    created_at: datetime
    last_updated: datetime
    expected_resolution: Optional[datetime]
    timeline: List[dict]  # List of status changes with timestamps
