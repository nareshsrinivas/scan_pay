#!/usr/bin/env python3
"""
QR Code Generator for Smart Checkout System
Generates both Product QR codes and Exit QR codes for testing
"""
import os
import qrcode
import json
import base64
from io import BytesIO
from datetime import datetime, timedelta

# Output directory for all QR codes
OUTPUT_DIR = "qr_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sample product data
SAMPLE_PRODUCTS = [
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Milk Tetra Pack",
        "sku": "MILK001",
        "price": 60.00
    },
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440002",
        "name": "Organic Oats",
        "sku": "OATS001",
        "price": 250.00
    },
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440003",
        "name": "Brown Bread",
        "sku": "BREAD001",
        "price": 45.00
    },
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440004",
        "name": "Fresh Eggs (Pack of 6)",
        "sku": "EGGS001",
        "price": 90.00
    }
]

def generate_product_qr(product):
    """Generate QR code for a product"""
    
    # Create QR data in the format expected by the system: PRODUCT:{sku}
    qr_data = f"PRODUCT:{product['sku']}"
    
    print(f"\n{'='*60}")
    print(f"📦 Generating Product QR Code")
    print(f"{'='*60}")
    print(f"Product: {product['name']}")
    print(f"SKU: {product['sku']}")
    print(f"Price: ₹{product['price']}")
    print(f"UUID: {product['uuid']}")
    print(f"\nQR Code Data: {qr_data}")
    
    # Create QR code object
    qr = qrcode.QRCode(
        version=1,  # Size of QR code (1-40)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
        box_size=10,  # Size of each box in pixels
        border=4,  # Border size in boxes
    )
    
    # Add data to QR code
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to file
    filename = os.path.join(OUTPUT_DIR, f"product_qr_{product['sku']}.png")
    img.save(filename)
    
    print(f"\n✅ QR Code Image saved: {filename}")
    print(f"📱 Customer scans this QR → Gets product details → Adds to cart")
    
    return filename, qr_data


def generate_exit_qr_demo():
    """
    Generate demo Exit QR code
    Note: In production, this uses JWT tokens from backend
    """
    
    # Sample order data
    order_data = {
        "order_uuid": "456e4567-e89b-12d3-a456-426614174222",
        "user_uuid": "550e8400-e29b-41d4-a716-446655440000",
        "total_amount": 126.00,
        "items_count": 2
    }
    
    # Create exit QR data (simplified for demo)
    # In production, this would be a signed JWT token
    exit_data = {
        "type": "exit",
        "order_uuid": order_data["order_uuid"],
        "total_amount": order_data["total_amount"],
        "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }
    
    print(f"\n{'='*60}")
    print(f"🎫 Generating Exit QR Code (Demo)")
    print(f"{'='*60}")
    print(f"Order UUID: {order_data['order_uuid']}")
    print(f"Total Amount: ₹{order_data['total_amount']}")
    print(f"Items: {order_data['items_count']}")
    print(f"\nExit QR Data (JSON):")
    print(json.dumps(exit_data, indent=2))
    print(f"\n⚠️  Note: In production, this is a signed JWT token")
    print(f"⏰ Expires: 10 minutes from creation")
    print(f"🔒 One-time use only")
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    
    # In production, this would be the JWT token string
    # For demo, we use JSON
    qr_content = json.dumps(exit_data)
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    # Create image with green fill (to distinguish from product QR)
    img = qr.make_image(fill_color="#13ec5b", back_color="white")
    
    # Save to file
    # filename = "exit_qr_demo.png"
    filename = os.path.join(OUTPUT_DIR, "exit_qr_demo.png")

    img.save(filename)
    
    print(f"\n✅ Exit QR Code saved: {filename}")
    print(f"👮 Staff scans this QR → Verifies payment → Customer exits")
    
    return filename, exit_data


def generate_qr_with_label(product):
    """Generate QR code with product label (for printing)"""
    from PIL import Image, ImageDraw, ImageFont
    
    # Generate base QR code with correct format: PRODUCT:{sku}
    qr_data = f"PRODUCT:{product['sku']}"
    
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Create new image with space for label
    qr_width, qr_height = qr_img.size
    label_height = 80
    final_img = Image.new('RGB', (qr_width, qr_height + label_height), 'white')
    
    # Paste QR code
    final_img.paste(qr_img, (0, 0))
    
    # Add text
    draw = ImageDraw.Draw(final_img)
    
    # Try to use a nice font, fall back to default if not available
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Product name
    text_y = qr_height + 10
    draw.text((qr_width//2, text_y), product['name'], fill='black', 
              font=font_large, anchor="mt")
    
    # SKU and Price
    text_y += 30
    draw.text((qr_width//2, text_y), f"{product['sku']} | ₹{product['price']}", 
              fill='black', font=font_small, anchor="mt")
    
    # Save
    # filename = f"product_label_{product['sku']}.png"
    filename = os.path.join(OUTPUT_DIR, f"product_label_{product['sku']}.png")

    final_img.save(filename)
    
    print(f"✅ Product Label saved: {filename}")
    return filename


def generate_all_qr_codes():
    """Generate all QR codes for testing"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║   Smart Checkout System - QR Code Generator                 ║
║   Generate Product and Exit QR Codes for Testing            ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    print("\n📦 GENERATING PRODUCT QR CODES")
    print("="*60)
    
    product_qrs = []
    for product in SAMPLE_PRODUCTS:
        filename, data = generate_product_qr(product)
        product_qrs.append(filename)
    
    print("\n\n🎫 GENERATING EXIT QR CODE (DEMO)")
    print("="*60)
    exit_filename, exit_data = generate_exit_qr_demo()
    
    print("\n\n🏷️  GENERATING PRODUCT LABELS (For Printing)")
    print("="*60)
    
    labels = []
    for product in SAMPLE_PRODUCTS:
        label_file = generate_qr_with_label(product)
        labels.append(label_file)
    
    # Summary
    print(f"\n\n{'='*60}")
    print("✅ GENERATION COMPLETE!")
    print(f"{'='*60}")
    print("\nGenerated Files:")
    print("\n📦 Product QR Codes (scan to add to cart):")
    for f in product_qrs:
        print(f"   • {f}")
    
    print("\n🏷️  Product Labels (for printing and sticking on products):")
    for f in labels:
        print(f"   • {f}")
    
    print(f"\n🎫 Exit QR Code (scan at gate to verify):")
    print(f"   • {exit_filename}")
    
    print("\n" + "="*60)
    print("HOW TO USE:")
    print("="*60)
    print("""
1️⃣  PRODUCT QR CODES:
   - Print product_qr_*.png files
   - Stick on actual products in store
   - Customer scans with phone camera
   - App fetches product details from backend
   - Customer adds to cart

2️⃣  PRODUCT LABELS:
   - Print product_label_*.png files
   - These include product name, SKU, and price
   - Stick on products for easy scanning

3️⃣  EXIT QR CODE:
   - This is generated AFTER customer pays
   - Customer shows on phone (not printed)
   - Staff scans at exit to verify payment
   - Valid for 10 minutes only
   - Can only be used once

4️⃣  TESTING:
   - Use any QR scanner app to test
   - Or use the React frontend's scanner
   - Scan product QR → see JSON data
   - That data is sent to backend API
""")
    
    print("\n📱 To test with the app:")
    print("   1. Start the system: docker-compose up -d")
    print("   2. Open frontend: http://localhost:3000")
    print("   3. Login as customer")
    print("   4. Go to 'Scan Product' page")
    print("   5. Scan any product_qr_*.png file")
    print("   6. Product details will appear!")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Check if qrcode is installed
    try:
        import qrcode
        from PIL import Image
    except ImportError:
        print("❌ Missing dependencies!")
        print("\nPlease install required packages:")
        print("pip install qrcode[pil] Pillow")
        exit(1)
    
    # Generate all QR codes
    generate_all_qr_codes()
    
    print("✨ All done! QR codes are ready for testing.\n")
