"""
Utility Functions for SUVIDHA
"""
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_otp,
    verify_otp,
)
from app.utils.encryption import (
    encrypt_data,
    decrypt_data,
    hash_data,
)
from app.utils.generators import (
    generate_tracking_id,
    generate_application_number,
    generate_receipt_number,
    generate_transaction_id,
    generate_qr_code,
)
from app.utils.audit import (
    create_audit_log,
    compute_log_hash,
)

__all__ = [
    # Security
    "hash_password", "verify_password",
    "create_access_token", "create_refresh_token", "verify_token",
    "generate_otp", "verify_otp",
    # Encryption
    "encrypt_data", "decrypt_data", "hash_data",
    # Generators
    "generate_tracking_id", "generate_application_number",
    "generate_receipt_number", "generate_transaction_id", "generate_qr_code",
    # Audit
    "create_audit_log", "compute_log_hash",
]
