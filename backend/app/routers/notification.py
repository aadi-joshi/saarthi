"""
Notification Router
- Get active notifications
- Banner notifications
- Advisories
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from typing import Optional, List
import json

from app.database import get_db
from app.models.notification import Notification, NotificationType
from app.schemas.notification import NotificationResponse, NotificationListResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=NotificationListResponse)
async def get_active_notifications(
    utility_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all active notifications for kiosk display"""
    now = datetime.utcnow()
    
    query = select(Notification).where(
        and_(
            Notification.is_active == True,
            Notification.start_time <= now,
            (Notification.end_time == None) | (Notification.end_time >= now)
        )
    )
    
    if utility_type:
        query = query.where(
            (Notification.utility_type == None) | 
            (Notification.utility_type == utility_type) |
            (Notification.utility_type == "all")
        )
    
    query = query.order_by(Notification.priority, Notification.start_time.desc())
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    # Parse affected areas JSON
    def parse_areas(n):
        if n.affected_areas:
            try:
                return json.loads(n.affected_areas)
            except:
                return []
        return None
    
    notification_responses = [
        NotificationResponse(
            id=n.id,
            title=n.title,
            title_hi=n.title_hi,
            message=n.message,
            message_hi=n.message_hi,
            notification_type=n.notification_type,
            priority=n.priority,
            utility_type=n.utility_type,
            affected_areas=parse_areas(n),
            is_banner=n.is_banner,
            start_time=n.start_time,
            end_time=n.end_time
        )
        for n in notifications
    ]
    
    # Separate banner notifications
    banner_notifications = [n for n in notification_responses if n.is_banner]
    
    # Count emergencies
    emergency_count = sum(1 for n in notifications if n.notification_type == NotificationType.EMERGENCY)
    
    return NotificationListResponse(
        notifications=notification_responses,
        banner_notifications=banner_notifications,
        emergency_count=emergency_count
    )


@router.get("/emergencies")
async def get_emergency_notifications(
    db: AsyncSession = Depends(get_db)
):
    """Get only emergency notifications"""
    now = datetime.utcnow()
    
    query = select(Notification).where(
        and_(
            Notification.is_active == True,
            Notification.notification_type == NotificationType.EMERGENCY,
            Notification.start_time <= now,
            (Notification.end_time == None) | (Notification.end_time >= now)
        )
    ).order_by(Notification.priority, Notification.start_time.desc())
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return {
        "emergencies": [
            {
                "id": n.id,
                "title": n.title,
                "title_hi": n.title_hi,
                "message": n.message,
                "message_hi": n.message_hi,
                "affected_areas": json.loads(n.affected_areas) if n.affected_areas else None,
                "start_time": n.start_time.isoformat()
            }
            for n in notifications
        ],
        "count": len(notifications)
    }


@router.get("/outages")
async def get_outage_notifications(
    utility_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get current outage notifications"""
    now = datetime.utcnow()
    
    query = select(Notification).where(
        and_(
            Notification.is_active == True,
            Notification.notification_type.in_([NotificationType.OUTAGE, NotificationType.MAINTENANCE]),
            Notification.start_time <= now,
            (Notification.end_time == None) | (Notification.end_time >= now)
        )
    )
    
    if utility_type:
        query = query.where(
            (Notification.utility_type == None) | (Notification.utility_type == utility_type)
        )
    
    query = query.order_by(Notification.priority)
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return {
        "outages": [
            {
                "id": n.id,
                "type": n.notification_type.value,
                "title": n.title,
                "title_hi": n.title_hi,
                "message": n.message,
                "message_hi": n.message_hi,
                "utility_type": n.utility_type,
                "affected_areas": json.loads(n.affected_areas) if n.affected_areas else None,
                "start_time": n.start_time.isoformat(),
                "expected_end": n.end_time.isoformat() if n.end_time else None
            }
            for n in notifications
        ],
        "count": len(notifications)
    }
