#!/usr/bin/env python3
"""
QR Code Generator from Database Products
Fetches products from the backend API and generates QR codes for them
"""
import os
import qrcode
import requests
import json
from PIL import Image, ImageDraw, ImageFont

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
OUTPUT_DIR = "qr_data_db"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_products_from_db():
    """Fetch all products from the database via API"""
    try:
        response = requests.get(f"{API_BASE_URL}/products", params={"limit": 100})
        response.raise_for_status()
        data = response.json()
        return data.get("products", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching products: {e}")
        print("\n💡 Make sure the backend server is running:")
        print("   cd backend && uvicorn app.main:app --reload")
        return []


def generate_product_qr(product):
    """Generate QR code for a product"""
    
    sku = product.get("sku", "UNKNOWN")
    name = product.get("name", "Unknown Product")
    price = product.get("price", 0)
    uuid = product.get("product_uuid", "N/A")
    
    # QR data format: PRODUCT:{sku}
    qr_data = f"PRODUCT:{sku}"
    
    print(f"\n📦 {name}")
    print(f"   SKU: {sku} | Price: ₹{price}")
    print(f"   QR Data: {qr_data}")
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    filename = os.path.join(OUTPUT_DIR, f"product_qr_{sku}.png")
    img.save(filename)
    
    print(f"   ✅ Saved: {filename}")
    
    return filename


def generate_product_label(product):
    """Generate QR code with product label for printing"""
    
    sku = product.get("sku", "UNKNOWN")
    name = product.get("name", "Unknown Product")
    price = product.get("price", 0)
    
    # QR data format: PRODUCT:{sku}
    qr_data = f"PRODUCT:{sku}"
    
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
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Truncate name if too long
    display_name = name[:25] + "..." if len(name) > 25 else name
    
    # Product name
    text_y = qr_height + 10
    draw.text((qr_width//2, text_y), display_name, fill='black', 
              font=font_large, anchor="mt")
    
    # SKU and Price
    text_y += 28
    draw.text((qr_width//2, text_y), f"{sku} | ₹{price}", 
              fill='gray', font=font_small, anchor="mt")
    
    filename = os.path.join(OUTPUT_DIR, f"product_label_{sku}.png")
    final_img.save(filename)
    
    return filename


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║   QR Code Generator - From Database Products                ║
║   Fetches products from API and generates QR codes          ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    print("🔄 Fetching products from database...")
    products = fetch_products_from_db()
    
    if not products:
        print("\n⚠️  No products found in database!")
        print("   Make sure to seed the database first.")
        return
    
    print(f"\n✅ Found {len(products)} products in database\n")
    print("="*60)
    print("📦 GENERATING QR CODES")
    print("="*60)
    
    qr_files = []
    label_files = []
    
    for product in products:
        qr_file = generate_product_qr(product)
        qr_files.append(qr_file)
        
        label_file = generate_product_label(product)
        label_files.append(label_file)
    
    # Summary
    print(f"\n\n{'='*60}")
    print("✅ GENERATION COMPLETE!")
    print(f"{'='*60}")
    
    print(f"\n📦 Generated {len(qr_files)} QR codes in '{OUTPUT_DIR}/' folder:")
    for f in qr_files:
        print(f"   • {f}")
    
    print(f"\n🏷️  Generated {len(label_files)} printable labels:")
    for f in label_files:
        print(f"   • {f}")
    
    print(f"""
{'='*60}
HOW TO USE:
{'='*60}
1. Print the product_label_*.png files
2. Stick them on actual products
3. Scan with the Scan & Pay app
4. Products will be added to cart!
{'='*60}
""")


if __name__ == "__main__":
    try:
        import qrcode
        import requests
        from PIL import Image
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("\nPlease install required packages:")
        print("pip install qrcode[pil] Pillow requests")
        exit(1)
    
    main()
