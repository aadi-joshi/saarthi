"""
Audit logging utilities with hash chain
"""
import hashlib
import json
from datetime import datetime
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc


async def get_last_log_hash(db: AsyncSession) -> Optional[str]:
    """Get hash of the last audit log entry"""
    from app.models.audit_log import AuditLog
    result = await db.execute(
        select(AuditLog.log_hash).order_by(desc(AuditLog.id)).limit(1)
    )
    row = result.scalar_one_or_none()
    return row


def compute_log_hash(
    action: str,
    actor_type: str,
    actor_id: Optional[int],
    resource_type: Optional[str],
    resource_id: Optional[int],
    timestamp: datetime,
    previous_hash: Optional[str],
    metadata: Optional[dict] = None
) -> str:
    """Compute SHA-256 hash for audit log entry (immutable chain)"""
    data = {
        "action": action,
        "actor_type": actor_type,
        "actor_id": actor_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "timestamp": timestamp.isoformat(),
        "previous_hash": previous_hash or "GENESIS",
        "metadata": metadata or {}
    }
    
    # Serialize deterministically
    json_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()


async def create_audit_log(
    db: AsyncSession,
    action: str,
    actor_type: str = "system",
    user_id: Optional[int] = None,
    admin_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    kiosk_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[dict] = None
) -> None:
    """Create an immutable audit log entry"""
    from app.models.audit_log import AuditLog, AuditAction
    
    # Get previous hash for chain
    previous_hash = await get_last_log_hash(db)
    
    # Compute hash for this entry
    timestamp = datetime.utcnow()
    actor_id = admin_id if actor_type == "admin" else user_id
    log_hash = compute_log_hash(
        action=action,
        actor_type=actor_type,
        actor_id=actor_id,
        resource_type=resource_type,
        resource_id=resource_id,
        timestamp=timestamp,
        previous_hash=previous_hash,
        metadata=metadata
    )
    
    # Create log entry
    log_entry = AuditLog(
        action=AuditAction(action) if action in AuditAction.__members__ else AuditAction.ADMIN_ACTION,
        description=description,
        user_id=user_id,
        admin_id=admin_id,
        actor_type=actor_type,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        kiosk_id=kiosk_id,
        session_id=session_id,
        metadata=json.dumps(metadata) if metadata else None,
        log_hash=log_hash,
        previous_hash=previous_hash,
        created_at=timestamp
    )
    
    db.add(log_entry)
    await db.flush()
