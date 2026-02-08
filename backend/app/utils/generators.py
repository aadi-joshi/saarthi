"""
ID and code generators
"""
import uuid
import io
import base64
from datetime import datetime
import qrcode


def generate_tracking_id(prefix: str = "GRV") -> str:
    """Generate grievance tracking ID: GRV2024010001"""
    now = datetime.utcnow()
    unique = uuid.uuid4().hex[:6].upper()
    return f"{prefix}{now.strftime('%Y%m')}{unique}"


def generate_application_number(prefix: str = "CON") -> str:
    """Generate connection application number: CON2024010001"""
    now = datetime.utcnow()
    unique = uuid.uuid4().hex[:6].upper()
    return f"{prefix}{now.strftime('%Y%m')}{unique}"


def generate_receipt_number() -> str:
    """Generate receipt number: RCP2024010100001"""
    now = datetime.utcnow()
    unique = uuid.uuid4().hex[:5].upper()
    return f"RCP{now.strftime('%Y%m%d')}{unique}"


def generate_transaction_id() -> str:
    """Generate transaction ID: TXN + timestamp + random"""
    now = datetime.utcnow()
    unique = uuid.uuid4().hex[:8].upper()
    return f"TXN{now.strftime('%Y%m%d%H%M%S')}{unique}"


def generate_session_id() -> str:
    """Generate kiosk session ID"""
    return f"SES_{uuid.uuid4().hex}"


def generate_qr_code(data: str, box_size: int = 10) -> str:
    """Generate QR code as base64 PNG"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()
    
    return f"data:image/png;base64,{img_base64}"


def generate_verification_url(tracking_id: str, base_url: str = "") -> str:
    """Generate verification URL for QR code"""
    if not base_url:
        base_url = "https://suvidha.gov.in"
    return f"{base_url}/verify/{tracking_id}"
