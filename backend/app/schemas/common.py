"""
Common Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error_code: str
    message: str
    details: Optional[Any] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response"""
    items: List[T]
    total: int
    page: int = 1
    page_size: int = 20
    total_pages: int
    has_next: bool
    has_previous: bool


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime
    database: str = "connected"
    cache: str = "connected"
