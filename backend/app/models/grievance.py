"""
Grievance Model - Citizen complaints and service requests
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class GrievanceCategory(str, enum.Enum):
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


class GrievanceStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class Grievance(Base):
    """
    Citizen grievance/complaint model with tracking
    """
    __tablename__ = "grievances"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Tracking
    tracking_id = Column(String(20), unique=True, index=True, nullable=False)  # e.g., GRV2024010001
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Grievance details
    category = Column(Enum(GrievanceCategory), nullable=False)
    sub_category = Column(String(100), nullable=True)
    subject = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    
    # Location (for field-based issues)
    location_address = Column(Text, nullable=True)
    location_landmark = Column(String(200), nullable=True)
    location_pin = Column(String(10), nullable=True)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # Reference
    related_account = Column(String(50), nullable=True)  # Consumer/Account number
    related_bill_id = Column(Integer, ForeignKey("bills.id"), nullable=True)
    
    # Status
    status = Column(Enum(GrievanceStatus), default=GrievanceStatus.SUBMITTED, nullable=False)
    priority = Column(Integer, default=3, nullable=False)  # 1=Critical, 2=High, 3=Medium, 4=Low
    
    # Assignment
    assigned_department = Column(String(100), nullable=True)
    assigned_officer = Column(String(200), nullable=True)
    
    # Resolution
    resolution_notes = Column(Text, nullable=True)
    resolution_date = Column(DateTime, nullable=True)
    citizen_feedback = Column(Integer, nullable=True)  # 1-5 rating
    citizen_feedback_comment = Column(Text, nullable=True)
    
    # SLA
    expected_resolution_date = Column(DateTime, nullable=True)
    escalation_level = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="grievances")
    documents = relationship("Document", back_populates="grievance", lazy="dynamic")
    
    def __repr__(self):
        return f"<Grievance(id={self.id}, tracking={self.tracking_id}, status={self.status})>"
