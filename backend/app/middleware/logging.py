"""
Request Logging Middleware
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("suvidha")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Start timer
        start_time = time.time()
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Log request
        logger.info(f"[{request_id}] {method} {path} - Client: {client_ip}")
        
        # Add request ID to state for access in routes
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"[{request_id}] {method} {path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
            
            # Add request ID header
            response.headers["X-Request-ID"] = request_id
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] {method} {path} - "
                f"Error: {str(e)} - "
                f"Duration: {duration:.3f}s"
            )
            raise
