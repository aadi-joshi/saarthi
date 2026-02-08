"""
Pydantic Schemas for SUVIDHA API
"""
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, OTPVerify, TokenResponse, TokenRefresh
)
from app.schemas.bill import (
    BillResponse, BillListResponse, BillPaymentRequest, PaymentResponse, PaymentHistoryResponse
)
from app.schemas.grievance import (
    GrievanceCreate, GrievanceUpdate, GrievanceResponse, GrievanceListResponse, GrievanceTrack
)
from app.schemas.connection import (
    ConnectionCreate, ConnectionUpdate, ConnectionResponse, ConnectionListResponse
)
from app.schemas.document import (
    DocumentUpload, DocumentResponse, DocumentListResponse
)
from app.schemas.notification import (
    NotificationResponse, NotificationListResponse
)
from app.schemas.admin import (
    AdminLogin, AdminCreate, AdminResponse, DashboardStats
)
from app.schemas.common import (
    SuccessResponse, ErrorResponse, PaginatedResponse
)

__all__ = [
    # User
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin", "OTPVerify", "TokenResponse", "TokenRefresh",
    # Bill
    "BillResponse", "BillListResponse", "BillPaymentRequest", "PaymentResponse", "PaymentHistoryResponse",
    # Grievance
    "GrievanceCreate", "GrievanceUpdate", "GrievanceResponse", "GrievanceListResponse", "GrievanceTrack",
    # Connection
    "ConnectionCreate", "ConnectionUpdate", "ConnectionResponse", "ConnectionListResponse",
    # Document
    "DocumentUpload", "DocumentResponse", "DocumentListResponse",
    # Notification
    "NotificationResponse", "NotificationListResponse",
    # Admin
    "AdminLogin", "AdminCreate", "AdminResponse", "DashboardStats",
    # Common
    "SuccessResponse", "ErrorResponse", "PaginatedResponse",
]
