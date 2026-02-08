"""
Notification Pydantic Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    OUTAGE = "outage"
    MAINTENANCE = "maintenance"
    ADVISORY = "advisory"
    EMERGENCY = "emergency"
    PAYMENT_REMINDER = "payment_reminder"
    SERVICE_UPDATE = "service_update"
    ANNOUNCEMENT = "announcement"


class NotificationResponse(BaseModel):
    """Notification details"""
    id: int
    title: str
    title_hi: Optional[str]
    message: str
    message_hi: Optional[str]
    notification_type: NotificationType
    priority: int
    utility_type: Optional[str]
    affected_areas: Optional[List[str]]
    is_banner: bool
    start_time: datetime
    end_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """List of notifications"""
    notifications: List[NotificationResponse]
    banner_notifications: List[NotificationResponse]
    emergency_count: int
