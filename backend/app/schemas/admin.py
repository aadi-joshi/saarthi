"""
Admin Pydantic Schemas
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal


class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AdminLogin(BaseModel):
    """Admin login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class AdminCreate(BaseModel):
    """Create admin user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    department: Optional[str] = None
    role: AdminRole = AdminRole.VIEWER


class AdminResponse(BaseModel):
    """Admin user response"""
    id: int
    username: str
    email: str
    full_name: str
    department: Optional[str]
    role: AdminRole
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Admin dashboard statistics"""
    # Overview
    total_users: int
    active_sessions: int
    total_transactions_today: int
    revenue_today: Decimal
    
    # Bills
    pending_bills: int
    overdue_bills: int
    bills_paid_today: int
    
    # Grievances
    total_grievances: int
    pending_grievances: int
    resolved_today: int
    avg_resolution_time_hours: float
    
    # Connections
    pending_connections: int
    connections_approved_today: int
    
    # Trends
    usage_by_service: dict  # {"electricity": 150, "gas": 45}
    usage_by_hour: List[int]  # 24 values for each hour
    grievance_by_category: dict
    
    # Kiosk stats
    kiosk_uptime_percent: float
    avg_session_duration_seconds: int
    drop_off_rate: float


class AnalyticsExport(BaseModel):
    """Analytics export request"""
    start_date: datetime
    end_date: datetime
    report_type: str  # usage, grievances, payments, connections
    format: str = "csv"  # csv, xlsx, pdf
