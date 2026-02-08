"""
Notification Model - System alerts and advisories
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer
from app.database import Base


class NotificationType(str, enum.Enum):
    OUTAGE = "outage"
    MAINTENANCE = "maintenance"
    ADVISORY = "advisory"
    EMERGENCY = "emergency"
    PAYMENT_REMINDER = "payment_reminder"
    SERVICE_UPDATE = "service_update"
    ANNOUNCEMENT = "announcement"


class Notification(Base):
    """
    System-wide notifications for kiosk display
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Content
    title = Column(String(200), nullable=False)
    title_hi = Column(String(200), nullable=True)  # Hindi translation
    message = Column(Text, nullable=False)
    message_hi = Column(Text, nullable=True)  # Hindi translation
    
    # Type and priority
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Integer, default=3, nullable=False)  # 1=Critical, 2=High, 3=Medium, 4=Low
    
    # Targeting
    utility_type = Column(String(50), nullable=True)  # electricity, gas, water, all
    affected_areas = Column(Text, nullable=True)  # JSON array of PIN codes or areas
    
    # Display settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_banner = Column(Boolean, default=False, nullable=False)  # Show as scrolling banner
    display_on_home = Column(Boolean, default=True, nullable=False)
    
    # Scheduling
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    
    # Metadata
    created_by = Column(Integer, nullable=True)  # Admin ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, title={self.title[:30]})>"
