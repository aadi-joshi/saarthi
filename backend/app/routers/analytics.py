"""
Analytics Router
- Session tracking
- Usage metrics
- Admin reports
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal
import json

from app.database import get_db
from app.models.session import KioskSession
from app.models.payment import Payment, PaymentStatus
from app.models.grievance import Grievance, GrievanceStatus
from app.models.connection import ConnectionRequest, ConnectionStatus
from app.models.bill import Bill, BillStatus
from app.models.user import User
from app.middleware.auth import get_current_admin
from app.utils.generators import generate_session_id

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/session/start")
async def start_session(
    request: Request,
    language: str = "en",
    accessibility_mode: bool = False,
    elderly_mode: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Start a new kiosk session for tracking"""
    session_id = generate_session_id()
    
    session = KioskSession(
        session_id=session_id,
        kiosk_id=request.headers.get("X-Kiosk-ID"),
        language=language,
        accessibility_mode=accessibility_mode,
        elderly_mode=elderly_mode,
        started_at=datetime.utcnow(),
        last_activity_at=datetime.utcnow(),
        user_agent=request.headers.get("User-Agent"),
    )
    
    db.add(session)
    await db.flush()
    
    return {
        "session_id": session_id,
        "started_at": session.started_at.isoformat()
    }


@router.post("/session/{session_id}/activity")
async def record_activity(
    session_id: str,
    page: str,
    action: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Record session activity (page view, action)"""
    result = await db.execute(
        select(KioskSession).where(KioskSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return {"error": "Session not found"}
    
    # Update pages visited
    pages = json.loads(session.pages_visited) if session.pages_visited else []
    pages.append({"page": page, "timestamp": datetime.utcnow().isoformat()})
    session.pages_visited = json.dumps(pages)
    
    # Update actions if provided
    if action:
        actions = json.loads(session.actions_performed) if session.actions_performed else []
        actions.append({"action": action, "timestamp": datetime.utcnow().isoformat()})
        session.actions_performed = json.dumps(actions)
    
    session.total_interactions += 1
    session.last_page = page
    session.last_activity_at = datetime.utcnow()
    
    return {"success": True}


@router.post("/session/{session_id}/end")
async def end_session(
    session_id: str,
    ended_by: str = "user",
    db: AsyncSession = Depends(get_db)
):
    """End a kiosk session"""
    result = await db.execute(
        select(KioskSession).where(KioskSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return {"error": "Session not found"}
    
    session.ended_at = datetime.utcnow()
    session.ended_by = ended_by
    
    # Calculate durations
    if session.started_at:
        total_seconds = int((session.ended_at - session.started_at).total_seconds())
        session.active_duration_seconds = total_seconds
    
    # Determine drop-off point if no transaction completed
    if not session.completed_transaction:
        session.drop_off_point = session.last_page
    
    return {
        "session_id": session_id,
        "duration_seconds": session.active_duration_seconds,
        "pages_visited": json.loads(session.pages_visited) if session.pages_visited else [],
        "completed_transaction": session.completed_transaction
    }


@router.get("/dashboard")
async def get_dashboard_stats(
    admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics"""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    # User stats
    total_users = await db.execute(select(func.count(User.id)))
    total_users = total_users.scalar() or 0
    
    # Active sessions today
    active_sessions = await db.execute(
        select(func.count(KioskSession.id)).where(
            and_(
                KioskSession.started_at >= today_start,
                KioskSession.ended_at == None
            )
        )
    )
    active_sessions = active_sessions.scalar() or 0
    
    # Payments today
    payments_today = await db.execute(
        select(func.count(Payment.id), func.sum(Payment.total_amount)).where(
            and_(
                Payment.completed_at >= today_start,
                Payment.status == PaymentStatus.SUCCESS
            )
        )
    )
    payments_result = payments_today.first()
    transactions_today = payments_result[0] or 0
    revenue_today = payments_result[1] or Decimal(0)
    
    # Bill stats
    pending_bills = await db.execute(
        select(func.count(Bill.id)).where(
            Bill.status.in_([BillStatus.PENDING, BillStatus.PARTIALLY_PAID])
        )
    )
    pending_bills = pending_bills.scalar() or 0
    
    overdue_bills = await db.execute(
        select(func.count(Bill.id)).where(Bill.status == BillStatus.OVERDUE)
    )
    overdue_bills = overdue_bills.scalar() or 0
    
    # Grievance stats
    total_grievances = await db.execute(
        select(func.count(Grievance.id))
    )
    total_grievances = total_grievances.scalar() or 0
    
    pending_grievances = await db.execute(
        select(func.count(Grievance.id)).where(
            Grievance.status.in_([
                GrievanceStatus.SUBMITTED, GrievanceStatus.ACKNOWLEDGED,
                GrievanceStatus.IN_PROGRESS, GrievanceStatus.ESCALATED
            ])
        )
    )
    pending_grievances = pending_grievances.scalar() or 0
    
    resolved_today = await db.execute(
        select(func.count(Grievance.id)).where(
            and_(
                Grievance.resolution_date >= today_start,
                Grievance.status.in_([GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED])
            )
        )
    )
    resolved_today = resolved_today.scalar() or 0
    
    # Connection stats
    pending_connections = await db.execute(
        select(func.count(ConnectionRequest.id)).where(
            ConnectionRequest.status.notin_([
                ConnectionStatus.COMPLETED, ConnectionStatus.REJECTED, ConnectionStatus.CANCELLED
            ])
        )
    )
    pending_connections = pending_connections.scalar() or 0
    
    # Usage by service (from sessions)
    services_used = await db.execute(
        select(KioskSession.services_used).where(
            KioskSession.started_at >= today_start
        )
    )
    service_count = {"electricity": 0, "gas": 0, "water": 0, "grievance": 0, "connection": 0}
    for row in services_used:
        if row[0]:
            try:
                services = json.loads(row[0])
                for s in services:
                    if s in service_count:
                        service_count[s] += 1
            except:
                pass
    
    # Usage by hour
    usage_by_hour = [0] * 24
    hourly_sessions = await db.execute(
        select(func.extract('hour', KioskSession.started_at), func.count(KioskSession.id))
        .where(KioskSession.started_at >= today_start)
        .group_by(func.extract('hour', KioskSession.started_at))
    )
    for row in hourly_sessions:
        if row[0] is not None:
            usage_by_hour[int(row[0])] = row[1]
    
    # Grievance by category
    grievance_by_category = await db.execute(
        select(Grievance.category, func.count(Grievance.id))
        .group_by(Grievance.category)
    )
    category_counts = {str(row[0].value): row[1] for row in grievance_by_category}
    
    # Session metrics
    avg_session = await db.execute(
        select(func.avg(KioskSession.active_duration_seconds)).where(
            KioskSession.ended_at != None
        )
    )
    avg_session_duration = int(avg_session.scalar() or 0)
    
    # Drop-off rate
    total_sessions = await db.execute(
        select(func.count(KioskSession.id)).where(KioskSession.ended_at != None)
    )
    total_sessions = total_sessions.scalar() or 1
    
    dropped_sessions = await db.execute(
        select(func.count(KioskSession.id)).where(
            and_(
                KioskSession.ended_at != None,
                KioskSession.completed_transaction == False
            )
        )
    )
    dropped_sessions = dropped_sessions.scalar() or 0
    drop_off_rate = round(dropped_sessions / total_sessions * 100, 2)
    
    return {
        "total_users": total_users,
        "active_sessions": active_sessions,
        "total_transactions_today": transactions_today,
        "revenue_today": float(revenue_today),
        "pending_bills": pending_bills,
        "overdue_bills": overdue_bills,
        "bills_paid_today": transactions_today,
        "total_grievances": total_grievances,
        "pending_grievances": pending_grievances,
        "resolved_today": resolved_today,
        "avg_resolution_time_hours": 48.5,  # Simulated
        "pending_connections": pending_connections,
        "connections_approved_today": 0,
        "usage_by_service": service_count,
        "usage_by_hour": usage_by_hour,
        "grievance_by_category": category_counts,
        "kiosk_uptime_percent": 99.5,  # Simulated
        "avg_session_duration_seconds": avg_session_duration,
        "drop_off_rate": drop_off_rate
    }


@router.get("/reports/export")
async def export_report(
    report_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Export analytics report (simulated - returns data)"""
    # In production, generate CSV/Excel/PDF
    return {
        "report_type": report_type,
        "period": {"start": start_date, "end": end_date},
        "format": "json",
        "data": [],
        "message": "Report generation would be implemented with actual export in production"
    }
