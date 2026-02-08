"""
Kiosk Session Model - Analytics and session tracking
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Numeric
from app.database import Base


class KioskSession(Base):
    """
    Kiosk interaction session for analytics
    """
    __tablename__ = "kiosk_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Session identification
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    kiosk_id = Column(String(50), nullable=True)  # Physical kiosk identifier
    
    # User association (optional - can be anonymous)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Session details
    language = Column(String(10), default="en", nullable=False)
    accessibility_mode = Column(Boolean, default=False, nullable=False)
    elderly_mode = Column(Boolean, default=False, nullable=False)
    
    # Navigation tracking (JSON array)
    pages_visited = Column(Text, nullable=True)  # ["home", "bills", "pay"]
    actions_performed = Column(Text, nullable=True)  # ["view_bill", "initiate_payment"]
    
    # Engagement metrics
    total_interactions = Column(Integer, default=0, nullable=False)
    active_duration_seconds = Column(Integer, default=0, nullable=False)
    idle_duration_seconds = Column(Integer, default=0, nullable=False)
    
    # Drop-off tracking
    last_page = Column(String(100), nullable=True)
    drop_off_point = Column(String(100), nullable=True)
    completed_transaction = Column(Boolean, default=False, nullable=False)
    
    # Outcome
    services_used = Column(Text, nullable=True)  # JSON array
    bills_paid = Column(Integer, default=0, nullable=False)
    grievances_filed = Column(Integer, default=0, nullable=False)
    connections_applied = Column(Integer, default=0, nullable=False)
    
    # Termination
    ended_by = Column(String(20), nullable=True)  # user, timeout, error, admin
    error_encountered = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Device info
    screen_resolution = Column(String(20), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<KioskSession(id={self.id}, session={self.session_id[:20]})>"
