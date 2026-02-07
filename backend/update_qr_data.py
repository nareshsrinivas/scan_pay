"""
Script to update product QR code data to use SKU format
"""
import sys

# Import Base first before any models
from app.database import Base, engine, SessionLocal

# Now import all models to register them with Base
from app.models.product import Product
from app.models.user import User
from app.models.cart import Cart
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.exit_qr import ExitQR
from app.models.staff import Staff

def update_product_qr_codes():
    """Update all products to use PRODUCT:{sku} format for qr_code_data"""
    print("🔄 Updating product QR code data...")
    
    # Create tables if needed
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        products = db.query(Product).all()
        print(f"Found {len(products)} products")
        
        for product in products:
            expected_qr = f"PRODUCT:{product.sku}"
            if product.qr_code_data != expected_qr:
                print(f"  Updating '{product.name}': '{product.qr_code_data}' -> '{expected_qr}'")
                product.qr_code_data = expected_qr
        
        db.commit()
        
        # Verify
        product = db.query(Product).first()
        if product:
            print(f"✅ Verified: SKU={product.sku}, qr_code_data={product.qr_code_data}")
        
        print("✅ Update complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    update_product_qr_codes()
