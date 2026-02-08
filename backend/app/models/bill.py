"""
Bill Model - Utility bills for electricity, gas, water
"""
import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from app.database import Base


class UtilityType(str, enum.Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"
    WATER = "water"
    SEWERAGE = "sewerage"
    PROPERTY_TAX = "property_tax"


class BillStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    DISPUTED = "disputed"


class Bill(Base):
    """
    Utility bill model
    """
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Bill identification
    bill_number = Column(String(50), unique=True, index=True, nullable=False)
    account_number = Column(String(50), index=True, nullable=False)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Bill details
    utility_type = Column(Enum(UtilityType), nullable=False)
    billing_period_start = Column(Date, nullable=False)
    billing_period_end = Column(Date, nullable=False)
    
    # Consumption
    previous_reading = Column(Numeric(12, 2), nullable=True)
    current_reading = Column(Numeric(12, 2), nullable=True)
    units_consumed = Column(Numeric(12, 2), nullable=True)
    
    # Amounts
    base_amount = Column(Numeric(12, 2), nullable=False)
    taxes = Column(Numeric(12, 2), default=0, nullable=False)
    surcharges = Column(Numeric(12, 2), default=0, nullable=False)
    late_fee = Column(Numeric(12, 2), default=0, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    amount_paid = Column(Numeric(12, 2), default=0, nullable=False)
    outstanding_amount = Column(Numeric(12, 2), nullable=False)
    
    # Dates
    bill_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    
    # Status
    status = Column(Enum(BillStatus), default=BillStatus.PENDING, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="bills")
    payments = relationship("Payment", back_populates="bill", lazy="dynamic")
    
    def __repr__(self):
        return f"<Bill(id={self.id}, number={self.bill_number}, amount={self.total_amount})>"
