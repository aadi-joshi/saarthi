"""
Payment Model - Transaction records with immutable hash chain
"""
import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class PaymentStatus(str, enum.Enum):
    INITIATED = "initiated"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    UPI = "upi"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    NET_BANKING = "net_banking"
    CASH = "cash"
    WALLET = "wallet"


class Payment(Base):
    """
    Payment transaction model with immutable hash chain for audit
    """
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Transaction identification
    transaction_id = Column(String(50), unique=True, index=True, nullable=False)
    gateway_transaction_id = Column(String(100), nullable=True)  # From payment gateway
    
    # Associations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=True, index=True)
    
    # Payment details
    amount = Column(Numeric(12, 2), nullable=False)
    convenience_fee = Column(Numeric(12, 2), default=0, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    
    # Status
    status = Column(Enum(PaymentStatus), default=PaymentStatus.INITIATED, nullable=False)
    failure_reason = Column(Text, nullable=True)
    
    # Receipt
    receipt_number = Column(String(50), unique=True, nullable=True)
    receipt_qr_code = Column(Text, nullable=True)  # Base64 encoded QR
    
    # Immutable hash chain for audit trail
    transaction_hash = Column(String(64), nullable=False)  # SHA256
    previous_hash = Column(String(64), nullable=True)  # Links to previous transaction
    
    # Timestamps
    initiated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Offline support
    is_offline = Column(Boolean, default=False, nullable=False)
    synced_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    bill = relationship("Bill", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, txn={self.transaction_id}, amount={self.total_amount}, status={self.status})>"
