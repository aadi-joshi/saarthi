"""
Authentication Router
- OTP-based login for citizens
- JWT token management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin, OTPVerify, TokenResponse, TokenRefresh, UserCreate, UserResponse
from app.utils.security import generate_otp, verify_otp, create_access_token, create_refresh_token, verify_token
from app.utils.encryption import encrypt_data, hash_data, mask_mobile
from app.utils.audit import create_audit_log
from app.middleware.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=dict)
async def request_otp(
    request: Request,
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Request OTP for mobile number login.
    If user doesn't exist, they will be created after OTP verification.
    """
    mobile_hash = hash_data(login_data.mobile)
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.mobile_hash == mobile_hash)
    )
    user = result.scalar_one_or_none()
    
    # Generate and send OTP
    otp = generate_otp(login_data.mobile)
    
    # In production, send OTP via SMS gateway
    # For demo, OTP is printed to console
    
    await create_audit_log(
        db=db,
        action="LOGIN",
        actor_type="user",
        user_id=user.id if user else None,
        description=f"OTP requested for mobile {mask_mobile(login_data.mobile)}",
        ip_address=request.client.host if request.client else None,
    )
    
    return {
        "success": True,
        "message": "OTP sent to your mobile number",
        "mobile_masked": mask_mobile(login_data.mobile),
        "otp_expires_in": settings.OTP_EXPIRE_MINUTES * 60,
        # For demo purposes only - remove in production
        "demo_otp": otp if settings.DEBUG else None
    }


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp_login(
    request: Request,
    verify_data: OTPVerify,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP and issue JWT tokens.
    Creates user account if new.
    """
    # Verify OTP
    if not verify_otp(verify_data.mobile, verify_data.otp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )
    
    mobile_hash = hash_data(verify_data.mobile)
    mobile_encrypted = encrypt_data(verify_data.mobile)
    
    # Find or create user
    result = await db.execute(
        select(User).where(User.mobile_hash == mobile_hash)
    )
    user = result.scalar_one_or_none()
    
    is_new_user = False
    if not user:
        # Create new user
        user = User(
            mobile_encrypted=mobile_encrypted,
            mobile_hash=mobile_hash,
            is_verified=True,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        is_new_user = True
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    # Create tokens
    token_data = {"sub": str(user.id), "user_type": "citizen"}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    await create_audit_log(
        db=db,
        action="LOGIN",
        actor_type="user",
        user_id=user.id,
        description="User logged in successfully",
        ip_address=request.client.host if request.client else None,
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        is_new_user=is_new_user
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")
    
    # Verify user still exists and is active
    result = await db.execute(
        select(User).where(User.id == int(user_id), User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    token_data = {"sub": str(user.id), "user_type": "citizen"}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    await create_audit_log(
        db=db,
        action="TOKEN_REFRESH",
        actor_type="user",
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        is_new_user=False
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    from app.utils.encryption import decrypt_data
    
    mobile = decrypt_data(user.mobile_encrypted)
    
    return UserResponse(
        id=user.id,
        consumer_number=user.consumer_number,
        full_name=user.full_name,
        mobile_masked=mask_mobile(mobile),
        role=user.role,
        preferred_language=user.preferred_language,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    request: Request,
    update_data: UserCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    from app.utils.encryption import decrypt_data
    
    # Update fields
    if update_data.full_name:
        user.full_name = update_data.full_name
    if update_data.email:
        user.email_encrypted = encrypt_data(update_data.email)
    if update_data.address:
        user.address_encrypted = encrypt_data(update_data.address)
    if update_data.consumer_number:
        user.consumer_number = update_data.consumer_number
    if update_data.preferred_language:
        user.preferred_language = update_data.preferred_language
    if update_data.aadhaar:
        user.aadhaar_encrypted = encrypt_data(update_data.aadhaar)
        user.aadhaar_hash = hash_data(update_data.aadhaar)
    
    await db.flush()
    
    mobile = decrypt_data(user.mobile_encrypted)
    
    return UserResponse(
        id=user.id,
        consumer_number=user.consumer_number,
        full_name=user.full_name,
        mobile_masked=mask_mobile(mobile),
        role=user.role,
        preferred_language=user.preferred_language,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.post("/logout")
async def logout(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user (invalidate session)"""
    await create_audit_log(
        db=db,
        action="LOGOUT",
        actor_type="user",
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    
    # In production, you would blacklist the token in Redis
    
    return {"success": True, "message": "Logged out successfully"}
