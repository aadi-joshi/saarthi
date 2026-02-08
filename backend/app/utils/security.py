"""
Security utilities - JWT, password hashing, OTP
"""
from datetime import datetime, timedelta
from typing import Optional, Any
import secrets
import hashlib
from jose import jwt, JWTError
from passlib.context import CryptContext
import redis

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis client for OTP storage
redis_client = None

def get_redis_client():
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception:
            # Fallback to in-memory storage for development
            redis_client = {}
    return redis_client


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None


def generate_otp(mobile: str) -> str:
    """Generate and store OTP for mobile number"""
    otp = ''.join([str(secrets.randbelow(10)) for _ in range(settings.OTP_LENGTH)])
    
    client = get_redis_client()
    otp_key = f"otp:{hashlib.sha256(mobile.encode()).hexdigest()}"
    
    if isinstance(client, dict):
        # In-memory fallback
        client[otp_key] = {"otp": otp, "expires": datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)}
    else:
        # Redis
        client.setex(otp_key, settings.OTP_EXPIRE_MINUTES * 60, otp)
    
    # In production, send OTP via SMS gateway
    print(f"[DEV] OTP for {mobile}: {otp}")  # Remove in production
    
    return otp


def verify_otp(mobile: str, otp: str) -> bool:
    """Verify OTP for mobile number"""
    client = get_redis_client()
    otp_key = f"otp:{hashlib.sha256(mobile.encode()).hexdigest()}"
    
    if isinstance(client, dict):
        # In-memory fallback
        stored = client.get(otp_key)
        if stored and stored["otp"] == otp and stored["expires"] > datetime.utcnow():
            del client[otp_key]
            return True
        return False
    else:
        # Redis
        stored_otp = client.get(otp_key)
        if stored_otp and stored_otp == otp:
            client.delete(otp_key)
            return True
        return False
