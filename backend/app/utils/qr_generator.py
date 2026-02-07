import qrcode
from io import BytesIO
import base64
from pathlib import Path
from typing import Optional

def generate_qr_code(data: str, save_path: Optional[str] = None) -> str:
    """
    Generate QR code from data
    Returns base64 encoded image string
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to file if path provided
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(save_path)
    
    # Convert to base64 for API response
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    
    return f"data:image/png;base64,{img_base64}"

def generate_product_qr(product_uuid: str, product_name: str) -> str:
    """Generate QR code for product scanning"""
    qr_data = f"PRODUCT:{product_uuid}"
    return generate_qr_code(qr_data)
