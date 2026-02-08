"""
Audit Log Model - Immutable action records for compliance
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Text, Integer
from app.database import Base


class AuditAction(str, enum.Enum):
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    TOKEN_REFRESH = "token_refresh"
    
    # Bills
    BILL_VIEW = "bill_view"
    BILL_PAYMENT_INITIATED = "bill_payment_initiated"
    BILL_PAYMENT_SUCCESS = "bill_payment_success"
    BILL_PAYMENT_FAILED = "bill_payment_failed"
    
    # Grievances
    GRIEVANCE_CREATED = "grievance_created"
    GRIEVANCE_UPDATED = "grievance_updated"
    GRIEVANCE_STATUS_CHANGED = "grievance_status_changed"
    
    # Connections
    CONNECTION_APPLIED = "connection_applied"
    CONNECTION_UPDATED = "connection_updated"
    CONNECTION_STATUS_CHANGED = "connection_status_changed"
    
    # Documents
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_VERIFIED = "document_verified"
    DOCUMENT_REJECTED = "document_rejected"
    DOCUMENT_DELETED = "document_deleted"
    
    # Admin
    ADMIN_LOGIN = "admin_login"
    ADMIN_ACTION = "admin_action"
    SETTINGS_CHANGED = "settings_changed"
    
    # System
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    SESSION_TIMEOUT = "session_timeout"
    
    # Data access
    PII_ACCESSED = "pii_accessed"
    DATA_EXPORTED = "data_exported"


class AuditLog(Base):
    """
    Immutable audit log with hash chain for tamper detection
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Action details
    action = Column(Enum(AuditAction), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Actor
    user_id = Column(Integer, nullable=True, index=True)
    admin_id = Column(Integer, nullable=True, index=True)
    actor_type = Column(String(20), nullable=False)  # user, admin, system
    
    # Context
    resource_type = Column(String(50), nullable=True)  # bill, grievance, etc.
    resource_id = Column(Integer, nullable=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    kiosk_id = Column(String(50), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Additional data (JSON)
    metadata = Column(Text, nullable=True)  # JSON string with additional context
    
    # Immutable hash chain
    log_hash = Column(String(64), nullable=False)  # SHA256
    previous_hash = Column(String(64), nullable=True)  # Links to previous log
    
    # Timestamp (immutable)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, actor={self.actor_type})>"
