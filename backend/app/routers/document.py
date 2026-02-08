"""
Document Router
- Upload documents
- View uploaded documents
- Validate documents
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from typing import Optional, List
import hashlib
import os
import uuid

from app.database import get_db
from app.models.user import User
from app.models.document import Document, DocumentType, DocumentStatus
from app.schemas.document import DocumentUpload, DocumentResponse, DocumentListResponse
from app.middleware.auth import get_current_user
from app.utils.audit import create_audit_log
from app.config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])


# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Check file type
    allowed_types = settings.ALLOWED_FILE_TYPES.split(",")
    extension = file.filename.split(".")[-1].lower() if file.filename else ""
    if extension not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    document_number: Optional[str] = Form(None),
    grievance_id: Optional[int] = Form(None),
    connection_request_id: Optional[int] = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document"""
    validate_file(file)
    
    # Generate unique filename
    extension = file.filename.split(".")[-1].lower() if file.filename else "bin"
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Read file content and compute hash
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check for duplicate
    existing = await db.execute(
        select(Document).where(
            and_(Document.user_id == user.id, Document.file_hash == file_hash)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This document has already been uploaded"
        )
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create document record
    document = Document(
        filename=unique_filename,
        original_filename=file.filename or "document",
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type or "application/octet-stream",
        file_hash=file_hash,
        document_type=document_type,
        document_number=document_number,
        user_id=user.id,
        grievance_id=grievance_id,
        connection_request_id=connection_request_id,
        status=DocumentStatus.UPLOADED,
    )
    
    db.add(document)
    await db.flush()
    
    await create_audit_log(
        db=db,
        action="DOCUMENT_UPLOADED",
        actor_type="user",
        user_id=user.id,
        resource_type="document",
        resource_id=document.id,
        description=f"Document uploaded: {document_type.value}",
        ip_address=request.client.host if request.client else None,
    )
    
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        original_filename=document.original_filename,
        document_type=document.document_type,
        document_number=document.document_number,
        file_size=document.file_size,
        mime_type=document.mime_type,
        status=document.status,
        verification_notes=None,
        rejection_reason=None,
        created_at=document.created_at,
        verified_at=None
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    document_type: Optional[DocumentType] = None,
    status_filter: Optional[DocumentStatus] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all documents for current user"""
    query = select(Document).where(Document.user_id == user.id)
    
    if document_type:
        query = query.where(Document.document_type == document_type)
    if status_filter:
        query = query.where(Document.status == status_filter)
    
    query = query.order_by(Document.created_at.desc())
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    verified_count = sum(1 for d in documents if d.status == DocumentStatus.VERIFIED)
    pending_count = sum(1 for d in documents if d.status in [DocumentStatus.UPLOADED, DocumentStatus.UNDER_REVIEW])
    
    document_responses = [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            original_filename=d.original_filename,
            document_type=d.document_type,
            document_number=d.document_number,
            file_size=d.file_size,
            mime_type=d.mime_type,
            status=d.status,
            verification_notes=d.verification_notes,
            rejection_reason=d.rejection_reason,
            created_at=d.created_at,
            verified_at=d.verified_at
        )
        for d in documents
    ]
    
    return DocumentListResponse(
        documents=document_responses,
        total=len(documents),
        verified_count=verified_count,
        pending_count=pending_count
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific document details"""
    result = await db.execute(
        select(Document).where(
            and_(Document.id == document_id, Document.user_id == user.id)
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        original_filename=document.original_filename,
        document_type=document.document_type,
        document_number=document.document_number,
        file_size=document.file_size,
        mime_type=document.mime_type,
        status=document.status,
        verification_notes=document.verification_notes,
        rejection_reason=document.rejection_reason,
        created_at=document.created_at,
        verified_at=document.verified_at
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an uploaded document"""
    result = await db.execute(
        select(Document).where(
            and_(Document.id == document_id, Document.user_id == user.id)
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.status == DocumentStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete verified documents"
        )
    
    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    await db.delete(document)
    
    await create_audit_log(
        db=db,
        action="DOCUMENT_DELETED",
        actor_type="user",
        user_id=user.id,
        resource_type="document",
        resource_id=document_id,
        ip_address=request.client.host if request.client else None,
    )
    
    return {"success": True, "message": "Document deleted"}
