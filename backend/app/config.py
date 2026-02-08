"""
SUVIDHA Backend Configuration
Smart Urban Virtual Interactive Digital Helpdesk Assistant
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SUVIDHA 2026"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://suvidha:suvidha@localhost:5432/suvidha"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_TO_A_LONG_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Encryption
    AES_KEY: str = "CHANGE_THIS_32_BYTE_KEY_IN_PROD!"  # Must be 32 bytes
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # OTP
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6
    
    # Session
    SESSION_TIMEOUT_MINUTES: int = 10
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = "pdf,jpg,jpeg,png"
    UPLOAD_DIR: str = "./uploads"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # External Services (Simulated)
    PAYMENT_GATEWAY_URL: str = "https://api.simulated-payment.local"
    SMS_GATEWAY_URL: str = "https://api.simulated-sms.local"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
