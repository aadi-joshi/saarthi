"""
Document Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    IDENTITY_PROOF = "identity_proof"
    ADDRESS_PROOF = "address_proof"
    PROPERTY_DOCUMENT = "property_document"
    PHOTOGRAPH = "photograph"
    SIGNATURE = "signature"
    NOC = "noc"
    PREVIOUS_BILL = "previous_bill"
    METER_PHOTO = "meter_photo"
    SITE_PHOTO = "site_photo"
    GRIEVANCE_ATTACHMENT = "grievance_attachment"
    OTHER = "other"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class DocumentUpload(BaseModel):
    """Document upload metadata"""
    document_type: DocumentType
    document_number: Optional[str] = None
    issued_by: Optional[str] = None
    issued_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    grievance_id: Optional[int] = None
    connection_request_id: Optional[int] = None


class DocumentResponse(BaseModel):
    """Document details response"""
    id: int
    filename: str
    original_filename: str
    document_type: DocumentType
    document_number: Optional[str]
    file_size: int
    mime_type: str
    status: DocumentStatus
    verification_notes: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    verified_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """List of documents"""
    documents: List[DocumentResponse]
    total: int
    verified_count: int
    pending_count: int
