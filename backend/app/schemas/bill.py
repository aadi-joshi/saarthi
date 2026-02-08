"""
Bill and Payment Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class UtilityType(str, Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"
    WATER = "water"
    SEWERAGE = "sewerage"
    PROPERTY_TAX = "property_tax"


class BillStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    DISPUTED = "disputed"


class PaymentMethod(str, Enum):
    UPI = "upi"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    NET_BANKING = "net_banking"
    CASH = "cash"
    WALLET = "wallet"


class BillResponse(BaseModel):
    """Bill details response"""
    id: int
    bill_number: str
    account_number: str
    utility_type: UtilityType
    billing_period_start: date
    billing_period_end: date
    units_consumed: Optional[Decimal]
    base_amount: Decimal
    taxes: Decimal
    surcharges: Decimal
    late_fee: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    outstanding_amount: Decimal
    bill_date: date
    due_date: date
    status: BillStatus
    is_overdue: bool = False
    days_until_due: Optional[int] = None
    
    class Config:
        from_attributes = True


class BillListResponse(BaseModel):
    """List of bills"""
    bills: List[BillResponse]
    total_outstanding: Decimal
    utility_summary: dict  # { "electricity": 1500, "gas": 500 }


class BillPaymentRequest(BaseModel):
    """Bill payment initiation"""
    bill_id: int
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethod
    return_url: Optional[str] = None  # For redirect after payment


class PaymentResponse(BaseModel):
    """Payment result"""
    transaction_id: str
    bill_id: int
    amount: Decimal
    status: str
    receipt_number: Optional[str]
    receipt_qr: Optional[str]  # Base64 QR code
    payment_time: datetime
    message: str
    
    class Config:
        from_attributes = True


class PaymentHistoryResponse(BaseModel):
    """Payment history item"""
    transaction_id: str
    bill_number: str
    utility_type: UtilityType
    amount: Decimal
    payment_method: PaymentMethod
    status: str
    payment_time: datetime
    receipt_number: Optional[str]
    
    class Config:
        from_attributes = True
