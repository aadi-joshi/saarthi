"""
Document Model - Uploaded files and certificates
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class DocumentType(str, enum.Enum):
    IDENTITY_PROOF = "identity_proof"
    ADDRESS_PROOF = "address_proof"
    PROPERTY_DOCUMENT = "property_document"
    PHOTOGRAPH = "photograph"
    SIGNATURE = "signature"
    NOC = "noc"  # No Objection Certificate
    PREVIOUS_BILL = "previous_bill"
    METER_PHOTO = "meter_photo"
    SITE_PHOTO = "site_photo"
    GRIEVANCE_ATTACHMENT = "grievance_attachment"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Document(Base):
    """
    Document/file upload model with validation tracking
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File details
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA256 for integrity
    
    # Document metadata
    document_type = Column(Enum(DocumentType), nullable=False)
    document_number = Column(String(100), nullable=True)  # e.g., Aadhaar number, etc.
    issued_by = Column(String(200), nullable=True)
    issued_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    # Associations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=True, index=True)
    connection_request_id = Column(Integer, ForeignKey("connection_requests.id"), nullable=True, index=True)
    
    # Status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    
    # Verification
    verified_by = Column(Integer, nullable=True)  # Admin ID
    verified_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    grievance = relationship("Grievance", back_populates="documents")
    connection_request = relationship("ConnectionRequest", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, type={self.document_type}, status={self.status})>"
