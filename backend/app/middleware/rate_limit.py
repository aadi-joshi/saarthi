"""
Rate Limiting Middleware
"""
import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis

from app.config import settings


class InMemoryRateLimiter:
    """Simple in-memory rate limiter for development"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """Check if request is allowed. Returns (allowed, remaining)"""
        current_time = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if t > current_time - window]
        
        if len(self.requests[key]) >= limit:
            return False, 0
        
        self.requests[key].append(current_time)
        return True, limit - len(self.requests[key])


class RedisRateLimiter:
    """Redis-based rate limiter for production"""
    
    def __init__(self, redis_url: str):
        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
        except Exception:
            self.redis = None
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """Check if request is allowed using sliding window"""
        if not self.redis:
            return True, limit
        
        try:
            pipe = self.redis.pipeline()
            now = time.time()
            
            # Use sorted set for sliding window
            rate_key = f"rate:{key}"
            
            pipe.zremrangebyscore(rate_key, 0, now - window)
            pipe.zadd(rate_key, {str(now): now})
            pipe.zcard(rate_key)
            pipe.expire(rate_key, window)
            
            results = pipe.execute()
            current_count = results[2]
            
            if current_count > limit:
                return False, 0
            
            return True, limit - current_count
        except Exception:
            # Fail open if Redis is down
            return True, limit


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = None):
        super().__init__(app)
        self.limit = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.window = 60  # 1 minute
        
        # Try Redis first, fallback to in-memory
        try:
            self.limiter = RedisRateLimiter(settings.REDIS_URL)
            if not self.limiter.redis:
                raise Exception("Redis not available")
        except Exception:
            self.limiter = InMemoryRateLimiter()
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier (IP or user ID)
        client_ip = request.client.host if request.client else "unknown"
        
        # Check authorization header for user-specific limiting
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            key = f"user:{auth_header[7:20]}"  # Use token prefix
        else:
            key = f"ip:{client_ip}"
        
        allowed, remaining = self.limiter.is_allowed(key, self.limit, self.window)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "X-RateLimit-Limit": str(self.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(self.window),
                    "Retry-After": str(self.window),
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
