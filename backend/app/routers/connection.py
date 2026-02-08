"""
Connection Request Router
- Apply for new connections
- Track application status
- Upload documents
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.connection import ConnectionRequest, ConnectionStatus, ConnectionType
from app.schemas.connection import (
    ConnectionCreate, ConnectionUpdate, ConnectionResponse, ConnectionListResponse
)
from app.middleware.auth import get_current_user
from app.utils.generators import generate_application_number
from app.utils.audit import create_audit_log

router = APIRouter(prefix="/connections", tags=["New Connections"])


# Fee structure (simulated)
FEE_STRUCTURE = {
    ConnectionType.ELECTRICITY_DOMESTIC: {
        "application_fee": Decimal("100"),
        "connection_fee": Decimal("1500"),
        "security_deposit": Decimal("500"),
    },
    ConnectionType.ELECTRICITY_COMMERCIAL: {
        "application_fee": Decimal("500"),
        "connection_fee": Decimal("5000"),
        "security_deposit": Decimal("2000"),
    },
    ConnectionType.ELECTRICITY_INDUSTRIAL: {
        "application_fee": Decimal("1000"),
        "connection_fee": Decimal("15000"),
        "security_deposit": Decimal("5000"),
    },
    ConnectionType.GAS_DOMESTIC: {
        "application_fee": Decimal("100"),
        "connection_fee": Decimal("2000"),
        "security_deposit": Decimal("500"),
    },
    ConnectionType.GAS_COMMERCIAL: {
        "application_fee": Decimal("500"),
        "connection_fee": Decimal("8000"),
        "security_deposit": Decimal("2000"),
    },
    ConnectionType.WATER_DOMESTIC: {
        "application_fee": Decimal("50"),
        "connection_fee": Decimal("1000"),
        "security_deposit": Decimal("300"),
    },
    ConnectionType.WATER_COMMERCIAL: {
        "application_fee": Decimal("200"),
        "connection_fee": Decimal("3000"),
        "security_deposit": Decimal("1000"),
    },
    ConnectionType.SEWERAGE: {
        "application_fee": Decimal("50"),
        "connection_fee": Decimal("800"),
        "security_deposit": Decimal("200"),
    },
}


@router.post("/apply", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_connection(
    request: Request,
    connection_data: ConnectionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Apply for a new utility connection"""
    application_number = generate_application_number("CON")
    
    # Calculate fees
    fees = FEE_STRUCTURE.get(connection_data.connection_type, {
        "application_fee": Decimal("100"),
        "connection_fee": Decimal("2000"),
        "security_deposit": Decimal("500"),
    })
    total_fee = fees["application_fee"] + fees["connection_fee"] + fees["security_deposit"]
    
    connection = ConnectionRequest(
        application_number=application_number,
        user_id=user.id,
        connection_type=connection_data.connection_type,
        load_requirement=connection_data.load_requirement,
        purpose=connection_data.purpose,
        applicant_name=connection_data.applicant_name,
        applicant_mobile=connection_data.applicant_mobile,
        applicant_email=connection_data.applicant_email,
        property_type=connection_data.property_type,
        property_address=connection_data.property_address,
        property_landmark=connection_data.property_landmark,
        property_pin=connection_data.property_pin,
        latitude=connection_data.latitude,
        longitude=connection_data.longitude,
        status=ConnectionStatus.SUBMITTED,
        current_step=1,
        total_steps=5,
        application_fee=fees["application_fee"],
        connection_fee=fees["connection_fee"],
        security_deposit=fees["security_deposit"],
        total_fee=total_fee,
        submitted_at=datetime.utcnow(),
    )
    
    db.add(connection)
    await db.flush()
    
    await create_audit_log(
        db=db,
        action="CONNECTION_APPLIED",
        actor_type="user",
        user_id=user.id,
        resource_type="connection",
        resource_id=connection.id,
        description=f"New connection application {application_number}",
        ip_address=request.client.host if request.client else None,
    )
    
    return ConnectionResponse(
        id=connection.id,
        application_number=application_number,
        connection_type=connection.connection_type,
        load_requirement=connection.load_requirement,
        applicant_name=connection.applicant_name,
        property_address=connection.property_address,
        property_pin=connection.property_pin,
        status=connection.status,
        current_step=connection.current_step,
        total_steps=connection.total_steps,
        application_fee=connection.application_fee,
        connection_fee=connection.connection_fee,
        security_deposit=connection.security_deposit,
        total_fee=connection.total_fee,
        fee_paid=connection.fee_paid,
        assigned_consumer_number=None,
        meter_number=None,
        rejection_reason=None,
        created_at=connection.created_at,
        updated_at=connection.updated_at,
        submitted_at=connection.submitted_at,
        completed_at=None
    )


@router.get("/", response_model=ConnectionListResponse)
async def list_connections(
    status_filter: Optional[ConnectionStatus] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all connection requests for current user"""
    query = select(ConnectionRequest).where(ConnectionRequest.user_id == user.id)
    
    if status_filter:
        query = query.where(ConnectionRequest.status == status_filter)
    
    query = query.order_by(ConnectionRequest.created_at.desc())
    
    result = await db.execute(query)
    connections = result.scalars().all()
    
    pending_statuses = [
        ConnectionStatus.SUBMITTED, ConnectionStatus.DOCUMENTS_PENDING,
        ConnectionStatus.DOCUMENTS_VERIFIED, ConnectionStatus.PAYMENT_PENDING,
        ConnectionStatus.PAYMENT_RECEIVED, ConnectionStatus.SITE_INSPECTION_PENDING,
        ConnectionStatus.SITE_INSPECTION_DONE, ConnectionStatus.APPROVED,
        ConnectionStatus.WORK_IN_PROGRESS
    ]
    
    pending_count = sum(1 for c in connections if c.status in pending_statuses)
    completed_count = sum(1 for c in connections if c.status == ConnectionStatus.COMPLETED)
    
    connection_responses = [
        ConnectionResponse(
            id=c.id,
            application_number=c.application_number,
            connection_type=c.connection_type,
            load_requirement=c.load_requirement,
            applicant_name=c.applicant_name,
            property_address=c.property_address,
            property_pin=c.property_pin,
            status=c.status,
            current_step=c.current_step,
            total_steps=c.total_steps,
            application_fee=c.application_fee,
            connection_fee=c.connection_fee,
            security_deposit=c.security_deposit,
            total_fee=c.total_fee,
            fee_paid=c.fee_paid,
            assigned_consumer_number=c.assigned_consumer_number,
            meter_number=c.meter_number,
            rejection_reason=c.rejection_reason,
            created_at=c.created_at,
            updated_at=c.updated_at,
            submitted_at=c.submitted_at,
            completed_at=c.completed_at
        )
        for c in connections
    ]
    
    return ConnectionListResponse(
        connections=connection_responses,
        total=len(connections),
        pending_count=pending_count,
        completed_count=completed_count
    )


@router.get("/{application_id}", response_model=ConnectionResponse)
async def get_connection_details(
    application_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific connection request details"""
    result = await db.execute(
        select(ConnectionRequest).where(
            and_(ConnectionRequest.id == application_id, ConnectionRequest.user_id == user.id)
        )
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection request not found"
        )
    
    return ConnectionResponse(
        id=connection.id,
        application_number=connection.application_number,
        connection_type=connection.connection_type,
        load_requirement=connection.load_requirement,
        applicant_name=connection.applicant_name,
        property_address=connection.property_address,
        property_pin=connection.property_pin,
        status=connection.status,
        current_step=connection.current_step,
        total_steps=connection.total_steps,
        application_fee=connection.application_fee,
        connection_fee=connection.connection_fee,
        security_deposit=connection.security_deposit,
        total_fee=connection.total_fee,
        fee_paid=connection.fee_paid,
        assigned_consumer_number=connection.assigned_consumer_number,
        meter_number=connection.meter_number,
        rejection_reason=connection.rejection_reason,
        created_at=connection.created_at,
        updated_at=connection.updated_at,
        submitted_at=connection.submitted_at,
        completed_at=connection.completed_at
    )


@router.get("/track/{application_number}")
async def track_connection(
    application_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Track connection application status by application number (public)"""
    result = await db.execute(
        select(ConnectionRequest).where(
            ConnectionRequest.application_number == application_number.upper()
        )
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Build step info
    steps = [
        {"step": 1, "name": "Application Submitted", "completed": connection.current_step >= 1},
        {"step": 2, "name": "Document Verification", "completed": connection.current_step >= 2},
        {"step": 3, "name": "Payment", "completed": connection.current_step >= 3},
        {"step": 4, "name": "Site Inspection", "completed": connection.current_step >= 4},
        {"step": 5, "name": "Connection Activation", "completed": connection.current_step >= 5},
    ]
    
    return {
        "application_number": connection.application_number,
        "connection_type": connection.connection_type.value,
        "status": connection.status.value,
        "current_step": connection.current_step,
        "total_steps": connection.total_steps,
        "steps": steps,
        "submitted_at": connection.submitted_at,
        "expected_completion": "15-30 working days from document verification"
    }
