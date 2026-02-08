"""
Grievance Router
- Submit complaints
- Track status
- View grievance history
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.grievance import Grievance, GrievanceStatus, GrievanceCategory
from app.schemas.grievance import (
    GrievanceCreate, GrievanceUpdate, GrievanceResponse, 
    GrievanceListResponse, GrievanceTrack
)
from app.middleware.auth import get_current_user, get_current_user_optional
from app.utils.generators import generate_tracking_id
from app.utils.audit import create_audit_log

router = APIRouter(prefix="/grievances", tags=["Grievances"])


# SLA definitions (hours)
SLA_BY_CATEGORY = {
    GrievanceCategory.GAS_LEAK: 4,  # Emergency - 4 hours
    GrievanceCategory.POWER_OUTAGE: 8,
    GrievanceCategory.WATER_SUPPLY: 24,
    GrievanceCategory.SEWERAGE: 24,
    GrievanceCategory.BILLING_DISPUTE: 72,
    GrievanceCategory.METER_ISSUE: 48,
    GrievanceCategory.STREET_LIGHT: 48,
    GrievanceCategory.GARBAGE_COLLECTION: 24,
    GrievanceCategory.ROAD_MAINTENANCE: 168,  # 7 days
    GrievanceCategory.PROPERTY_TAX: 72,
    GrievanceCategory.STAFF_BEHAVIOUR: 72,
    GrievanceCategory.SERVICE_DELAY: 48,
    GrievanceCategory.OTHER: 72,
}


@router.post("/", response_model=GrievanceResponse, status_code=status.HTTP_201_CREATED)
async def create_grievance(
    request: Request,
    grievance_data: GrievanceCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a new grievance/complaint"""
    tracking_id = generate_tracking_id("GRV")
    
    # Calculate expected resolution based on SLA
    sla_hours = SLA_BY_CATEGORY.get(grievance_data.category, 72)
    expected_resolution = datetime.utcnow() + timedelta(hours=sla_hours)
    
    # Determine priority based on category
    priority = 3  # Default: Medium
    if grievance_data.category in [GrievanceCategory.GAS_LEAK]:
        priority = 1  # Critical
    elif grievance_data.category in [GrievanceCategory.POWER_OUTAGE, GrievanceCategory.WATER_SUPPLY]:
        priority = 2  # High
    
    # Determine assigned department
    department_map = {
        GrievanceCategory.POWER_OUTAGE: "Electricity Department",
        GrievanceCategory.METER_ISSUE: "Electricity Department",
        GrievanceCategory.BILLING_DISPUTE: "Billing Department",
        GrievanceCategory.GAS_LEAK: "Gas Department",
        GrievanceCategory.WATER_SUPPLY: "Water Department",
        GrievanceCategory.SEWERAGE: "Sewerage Department",
        GrievanceCategory.STREET_LIGHT: "Municipal Corporation",
        GrievanceCategory.GARBAGE_COLLECTION: "Sanitation Department",
        GrievanceCategory.ROAD_MAINTENANCE: "Public Works Department",
        GrievanceCategory.PROPERTY_TAX: "Revenue Department",
    }
    assigned_department = department_map.get(grievance_data.category, "General Services")
    
    grievance = Grievance(
        tracking_id=tracking_id,
        user_id=user.id,
        category=grievance_data.category,
        sub_category=grievance_data.sub_category,
        subject=grievance_data.subject,
        description=grievance_data.description,
        location_address=grievance_data.location_address,
        location_landmark=grievance_data.location_landmark,
        location_pin=grievance_data.location_pin,
        latitude=grievance_data.latitude,
        longitude=grievance_data.longitude,
        related_account=grievance_data.related_account,
        related_bill_id=grievance_data.related_bill_id,
        status=GrievanceStatus.SUBMITTED,
        priority=priority,
        assigned_department=assigned_department,
        expected_resolution_date=expected_resolution,
    )
    
    db.add(grievance)
    await db.flush()
    
    await create_audit_log(
        db=db,
        action="GRIEVANCE_CREATED",
        actor_type="user",
        user_id=user.id,
        resource_type="grievance",
        resource_id=grievance.id,
        description=f"Grievance {tracking_id} created - {grievance_data.category.value}",
        ip_address=request.client.host if request.client else None,
    )
    
    return GrievanceResponse(
        id=grievance.id,
        tracking_id=tracking_id,
        category=grievance.category,
        sub_category=grievance.sub_category,
        subject=grievance.subject,
        description=grievance.description,
        location_address=grievance.location_address,
        status=grievance.status,
        priority=grievance.priority,
        assigned_department=grievance.assigned_department,
        expected_resolution_date=grievance.expected_resolution_date,
        resolution_notes=None,
        created_at=grievance.created_at,
        updated_at=grievance.updated_at,
        acknowledged_at=None
    )


@router.get("/", response_model=GrievanceListResponse)
async def list_grievances(
    status_filter: Optional[GrievanceStatus] = None,
    category: Optional[GrievanceCategory] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all grievances for current user"""
    query = select(Grievance).where(Grievance.user_id == user.id)
    
    if status_filter:
        query = query.where(Grievance.status == status_filter)
    if category:
        query = query.where(Grievance.category == category)
    
    query = query.order_by(Grievance.created_at.desc())
    
    result = await db.execute(query)
    grievances = result.scalars().all()
    
    # Count by status
    pending_count = sum(1 for g in grievances if g.status in [
        GrievanceStatus.SUBMITTED, GrievanceStatus.ACKNOWLEDGED, 
        GrievanceStatus.IN_PROGRESS, GrievanceStatus.ESCALATED
    ])
    resolved_count = sum(1 for g in grievances if g.status in [
        GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED
    ])
    
    grievance_responses = [
        GrievanceResponse(
            id=g.id,
            tracking_id=g.tracking_id,
            category=g.category,
            sub_category=g.sub_category,
            subject=g.subject,
            description=g.description,
            location_address=g.location_address,
            status=g.status,
            priority=g.priority,
            assigned_department=g.assigned_department,
            expected_resolution_date=g.expected_resolution_date,
            resolution_notes=g.resolution_notes,
            created_at=g.created_at,
            updated_at=g.updated_at,
            acknowledged_at=g.acknowledged_at
        )
        for g in grievances
    ]
    
    return GrievanceListResponse(
        grievances=grievance_responses,
        total=len(grievances),
        pending_count=pending_count,
        resolved_count=resolved_count
    )


@router.get("/track/{tracking_id}", response_model=GrievanceTrack)
async def track_grievance(
    tracking_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Track grievance status by tracking ID (public endpoint)"""
    result = await db.execute(
        select(Grievance).where(Grievance.tracking_id == tracking_id.upper())
    )
    grievance = result.scalar_one_or_none()
    
    if not grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grievance not found. Please check tracking ID."
        )
    
    # Build timeline
    timeline = [
        {
            "status": "SUBMITTED",
            "description": "Grievance submitted",
            "timestamp": grievance.created_at.isoformat(),
            "completed": True
        }
    ]
    
    if grievance.acknowledged_at:
        timeline.append({
            "status": "ACKNOWLEDGED",
            "description": f"Acknowledged by {grievance.assigned_department}",
            "timestamp": grievance.acknowledged_at.isoformat(),
            "completed": True
        })
    
    if grievance.status in [GrievanceStatus.IN_PROGRESS, GrievanceStatus.ESCALATED, 
                            GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED]:
        timeline.append({
            "status": "IN_PROGRESS",
            "description": "Being processed",
            "timestamp": grievance.updated_at.isoformat(),
            "completed": True
        })
    
    if grievance.status in [GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED]:
        timeline.append({
            "status": "RESOLVED",
            "description": grievance.resolution_notes or "Issue resolved",
            "timestamp": grievance.resolution_date.isoformat() if grievance.resolution_date else grievance.updated_at.isoformat(),
            "completed": True
        })
    
    # Status descriptions
    status_descriptions = {
        GrievanceStatus.SUBMITTED: "Your grievance has been registered and is awaiting acknowledgment",
        GrievanceStatus.ACKNOWLEDGED: "Your grievance has been acknowledged and assigned to the relevant department",
        GrievanceStatus.IN_PROGRESS: "Work is in progress to resolve your grievance",
        GrievanceStatus.ESCALATED: "Your grievance has been escalated to higher authorities",
        GrievanceStatus.RESOLVED: "Your grievance has been resolved",
        GrievanceStatus.CLOSED: "Your grievance has been closed",
        GrievanceStatus.REJECTED: "Your grievance has been rejected"
    }
    
    return GrievanceTrack(
        tracking_id=grievance.tracking_id,
        status=grievance.status,
        status_description=status_descriptions.get(grievance.status, "Processing"),
        created_at=grievance.created_at,
        last_updated=grievance.updated_at,
        expected_resolution=grievance.expected_resolution_date,
        timeline=timeline
    )


@router.get("/{grievance_id}", response_model=GrievanceResponse)
async def get_grievance_details(
    grievance_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific grievance details"""
    result = await db.execute(
        select(Grievance).where(
            and_(Grievance.id == grievance_id, Grievance.user_id == user.id)
        )
    )
    grievance = result.scalar_one_or_none()
    
    if not grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grievance not found"
        )
    
    return GrievanceResponse(
        id=grievance.id,
        tracking_id=grievance.tracking_id,
        category=grievance.category,
        sub_category=grievance.sub_category,
        subject=grievance.subject,
        description=grievance.description,
        location_address=grievance.location_address,
        status=grievance.status,
        priority=grievance.priority,
        assigned_department=grievance.assigned_department,
        expected_resolution_date=grievance.expected_resolution_date,
        resolution_notes=grievance.resolution_notes,
        created_at=grievance.created_at,
        updated_at=grievance.updated_at,
        acknowledged_at=grievance.acknowledged_at
    )


@router.post("/{grievance_id}/feedback")
async def submit_feedback(
    grievance_id: int,
    feedback: GrievanceUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback for resolved grievance"""
    result = await db.execute(
        select(Grievance).where(
            and_(
                Grievance.id == grievance_id, 
                Grievance.user_id == user.id,
                Grievance.status.in_([GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED])
            )
        )
    )
    grievance = result.scalar_one_or_none()
    
    if not grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grievance not found or not yet resolved"
        )
    
    if feedback.feedback:
        grievance.citizen_feedback = feedback.feedback
    if feedback.feedback_comment:
        grievance.citizen_feedback_comment = feedback.feedback_comment
    
    await db.flush()
    
    return {"success": True, "message": "Feedback submitted successfully"}
