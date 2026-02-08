"""
Encryption utilities - AES encryption for PII
"""
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings


def _get_fernet_key() -> bytes:
    """Derive Fernet key from AES key"""
    # Ensure key is 32 bytes for Fernet
    key = settings.AES_KEY.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"suvidha_salt_v1",  # Static salt - in production, use unique salts per field
        iterations=100000,
    )
    derived_key = base64.urlsafe_b64encode(kdf.derive(key))
    return derived_key


_fernet = None


def _get_fernet():
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_get_fernet_key())
    return _fernet


def encrypt_data(plaintext: str) -> str:
    """Encrypt sensitive data using AES (Fernet)"""
    if not plaintext:
        return ""
    fernet = _get_fernet()
    encrypted = fernet.encrypt(plaintext.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(ciphertext: str) -> str:
    """Decrypt sensitive data"""
    if not ciphertext:
        return ""
    fernet = _get_fernet()
    try:
        encrypted = base64.urlsafe_b64decode(ciphertext.encode())
        decrypted = fernet.decrypt(encrypted)
        return decrypted.decode()
    except Exception:
        return ""


def hash_data(data: str) -> str:
    """Create SHA-256 hash for lookups (non-reversible)"""
    if not data:
        return ""
    return hashlib.sha256(data.encode()).hexdigest()


def mask_mobile(mobile: str) -> str:
    """Mask mobile number for display: ******1234"""
    if not mobile or len(mobile) < 4:
        return "****"
    return "*" * (len(mobile) - 4) + mobile[-4:]


def mask_aadhaar(aadhaar: str) -> str:
    """Mask Aadhaar for display: XXXX-XXXX-1234"""
    if not aadhaar or len(aadhaar) != 12:
        return "XXXX-XXXX-XXXX"
    return f"XXXX-XXXX-{aadhaar[-4:]}"
