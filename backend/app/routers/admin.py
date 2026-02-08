"""
Admin Router
- Admin authentication
- User management
- Grievance management
- System settings
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime
from typing import Optional, List

from app.database import get_db
from app.models.admin import Admin, AdminRole
from app.models.grievance import Grievance, GrievanceStatus
from app.models.connection import ConnectionRequest, ConnectionStatus
from app.models.notification import Notification, NotificationType
from app.schemas.admin import AdminLogin, AdminCreate, AdminResponse
from app.middleware.auth import get_current_admin
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.utils.audit import create_audit_log
from app.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login")
async def admin_login(
    request: Request,
    login_data: AdminLogin,
    db: AsyncSession = Depends(get_db)
):
    """Admin login with username/password"""
    result = await db.execute(
        select(Admin).where(
            and_(Admin.username == login_data.username, Admin.is_active == True)
        )
    )
    admin = result.scalar_one_or_none()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if locked
    if admin.locked_until and admin.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked. Try again later."
        )
    
    # Verify password
    if not verify_password(login_data.password, admin.password_hash):
        admin.failed_login_attempts += 1
        
        # Lock after 5 failed attempts
        if admin.failed_login_attempts >= 5:
            from datetime import timedelta
            admin.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        await db.flush()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Reset failed attempts
    admin.failed_login_attempts = 0
    admin.locked_until = None
    admin.last_login = datetime.utcnow()
    
    # Create tokens
    token_data = {
        "sub": str(admin.id),
        "user_type": "admin",
        "role": admin.role.value
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    await create_audit_log(
        db=db,
        action="ADMIN_LOGIN",
        actor_type="admin",
        admin_id=admin.id,
        description=f"Admin {admin.username} logged in",
        ip_address=request.client.host if request.client else None,
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "full_name": admin.full_name,
            "role": admin.role.value,
            "department": admin.department
        }
    }


@router.get("/me", response_model=AdminResponse)
async def get_admin_profile(
    admin: Admin = Depends(get_current_admin)
):
    """Get current admin profile"""
    return AdminResponse(
        id=admin.id,
        username=admin.username,
        email=admin.email,
        full_name=admin.full_name,
        department=admin.department,
        role=admin.role,
        is_active=admin.is_active,
        last_login=admin.last_login,
        created_at=admin.created_at
    )


@router.get("/grievances")
async def list_all_grievances(
    status_filter: Optional[GrievanceStatus] = None,
    department: Optional[str] = None,
    priority: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all grievances for admin management"""
    query = select(Grievance)
    
    # Filter by admin's department if not super admin
    if admin.role != AdminRole.SUPER_ADMIN and admin.department:
        query = query.where(Grievance.assigned_department == admin.department)
    
    if status_filter:
        query = query.where(Grievance.status == status_filter)
    if department:
        query = query.where(Grievance.assigned_department == department)
    if priority:
        query = query.where(Grievance.priority == priority)
    
    query = query.order_by(Grievance.priority, Grievance.created_at.desc())
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    grievances = result.scalars().all()
    
    return {
        "grievances": [
            {
                "id": g.id,
                "tracking_id": g.tracking_id,
                "category": g.category.value,
                "subject": g.subject,
                "status": g.status.value,
                "priority": g.priority,
                "assigned_department": g.assigned_department,
                "created_at": g.created_at.isoformat(),
                "expected_resolution": g.expected_resolution_date.isoformat() if g.expected_resolution_date else None
            }
            for g in grievances
        ],
        "total": len(grievances)
    }


@router.put("/grievances/{grievance_id}/status")
async def update_grievance_status(
    grievance_id: int,
    request: Request,
    new_status: GrievanceStatus,
    resolution_notes: Optional[str] = None,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update grievance status"""
    result = await db.execute(
        select(Grievance).where(Grievance.id == grievance_id)
    )
    grievance = result.scalar_one_or_none()
    
    if not grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grievance not found"
        )
    
    old_status = grievance.status
    grievance.status = new_status
    
    if new_status == GrievanceStatus.ACKNOWLEDGED and not grievance.acknowledged_at:
        grievance.acknowledged_at = datetime.utcnow()
    
    if new_status in [GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED]:
        grievance.resolution_date = datetime.utcnow()
        if resolution_notes:
            grievance.resolution_notes = resolution_notes
    
    await create_audit_log(
        db=db,
        action="GRIEVANCE_STATUS_CHANGED",
        actor_type="admin",
        admin_id=admin.id,
        resource_type="grievance",
        resource_id=grievance_id,
        description=f"Status changed from {old_status.value} to {new_status.value}",
        ip_address=request.client.host if request.client else None,
    )
    
    return {
        "success": True,
        "grievance_id": grievance_id,
        "tracking_id": grievance.tracking_id,
        "old_status": old_status.value,
        "new_status": new_status.value
    }


@router.get("/connections")
async def list_all_connections(
    status_filter: Optional[ConnectionStatus] = None,
    limit: int = 50,
    offset: int = 0,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all connection requests for admin"""
    query = select(ConnectionRequest)
    
    if status_filter:
        query = query.where(ConnectionRequest.status == status_filter)
    
    query = query.order_by(ConnectionRequest.created_at.desc())
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    connections = result.scalars().all()
    
    return {
        "connections": [
            {
                "id": c.id,
                "application_number": c.application_number,
                "connection_type": c.connection_type.value,
                "applicant_name": c.applicant_name,
                "status": c.status.value,
                "current_step": c.current_step,
                "fee_paid": c.fee_paid,
                "created_at": c.created_at.isoformat()
            }
            for c in connections
        ],
        "total": len(connections)
    }


@router.put("/connections/{connection_id}/status")
async def update_connection_status(
    connection_id: int,
    request: Request,
    new_status: ConnectionStatus,
    notes: Optional[str] = None,
    consumer_number: Optional[str] = None,
    meter_number: Optional[str] = None,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update connection request status"""
    result = await db.execute(
        select(ConnectionRequest).where(ConnectionRequest.id == connection_id)
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection request not found"
        )
    
    old_status = connection.status
    connection.status = new_status
    
    # Update step based on status
    status_to_step = {
        ConnectionStatus.SUBMITTED: 1,
        ConnectionStatus.DOCUMENTS_PENDING: 1,
        ConnectionStatus.DOCUMENTS_VERIFIED: 2,
        ConnectionStatus.PAYMENT_PENDING: 2,
        ConnectionStatus.PAYMENT_RECEIVED: 3,
        ConnectionStatus.SITE_INSPECTION_PENDING: 3,
        ConnectionStatus.SITE_INSPECTION_DONE: 4,
        ConnectionStatus.APPROVED: 4,
        ConnectionStatus.WORK_IN_PROGRESS: 4,
        ConnectionStatus.COMPLETED: 5,
    }
    connection.current_step = status_to_step.get(new_status, connection.current_step)
    
    if new_status == ConnectionStatus.COMPLETED:
        connection.completed_at = datetime.utcnow()
        if consumer_number:
            connection.assigned_consumer_number = consumer_number
        if meter_number:
            connection.meter_number = meter_number
    
    if new_status == ConnectionStatus.REJECTED and notes:
        connection.rejection_reason = notes
    
    await create_audit_log(
        db=db,
        action="CONNECTION_STATUS_CHANGED",
        actor_type="admin",
        admin_id=admin.id,
        resource_type="connection",
        resource_id=connection_id,
        description=f"Status changed from {old_status.value} to {new_status.value}",
        ip_address=request.client.host if request.client else None,
    )
    
    return {
        "success": True,
        "connection_id": connection_id,
        "old_status": old_status.value,
        "new_status": new_status.value
    }


@router.post("/notifications")
async def create_notification(
    request: Request,
    title: str,
    message: str,
    notification_type: NotificationType,
    title_hi: Optional[str] = None,
    message_hi: Optional[str] = None,
    utility_type: Optional[str] = None,
    is_banner: bool = False,
    priority: int = 3,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new notification"""
    notification = Notification(
        title=title,
        title_hi=title_hi,
        message=message,
        message_hi=message_hi,
        notification_type=notification_type,
        priority=priority,
        utility_type=utility_type,
        is_banner=is_banner,
        display_on_home=True,
        start_time=datetime.utcnow(),
        created_by=admin.id,
    )
    
    db.add(notification)
    await db.flush()
    
    return {
        "success": True,
        "notification_id": notification.id,
        "message": "Notification created successfully"
    }
