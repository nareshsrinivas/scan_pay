"""
Seed script to populate database with sample products and staff
Run: python -m app.seed
"""

from app.database import SessionLocal, init_db
from app.models.product import Product
from app.models.staff import Staff
from app.core.security import hash_password
import random

def seed_products(db):
    """Seed sample products"""
    products_data = [
        {
            "name": "Milk Tetra Pack",
            "sku": "MILK001",
            "description": "Fresh full cream milk 1L",
            "price": 60.00,
            "stock": 100,
            "category": "Dairy",
            "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400"
        },
        {
            "name": "Organic Oats",
            "sku": "OATS002",
            "description": "100% organic rolled oats 500g",
            "price": 250.00,
            "stock": 50,
            "category": "Breakfast",
            "image_url": "https://images.unsplash.com/photo-1574856344991-aaa31b6f4ce3?w=400"
        },
        {
            "name": "Whole Wheat Bread",
            "sku": "BREAD003",
            "description": "Fresh whole wheat bread loaf",
            "price": 45.00,
            "stock": 75,
            "category": "Bakery",
            "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400"
        },
        {
            "name": "Organic Bananas",
            "sku": "BANANA004",
            "description": "Fresh organic bananas 1kg",
            "price": 80.00,
            "stock": 120,
            "category": "Fruits",
            "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400"
        },
        {
            "name": "Free Range Eggs",
            "sku": "EGGS005",
            "description": "Farm fresh free range eggs - 12 pack",
            "price": 120.00,
            "stock": 60,
            "category": "Dairy",
            "image_url": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400"
        },
        {
            "name": "Olive Oil",
            "sku": "OIL006",
            "description": "Extra virgin olive oil 500ml",
            "price": 450.00,
            "stock": 40,
            "category": "Cooking",
            "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400"
        },
        {
            "name": "Greek Yogurt",
            "sku": "YOGURT007",
            "description": "Rich and creamy Greek yogurt 500g",
            "price": 150.00,
            "stock": 80,
            "category": "Dairy",
            "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400"
        },
        {
            "name": "Granola Mix",
            "sku": "GRANOLA008",
            "description": "Crunchy granola with nuts and honey 400g",
            "price": 280.00,
            "stock": 45,
            "category": "Breakfast",
            "image_url": "https://images.unsplash.com/photo-1526318896980-cf78c088247c?w=400"
        },
        {
            "name": "Almond Milk",
            "sku": "ALMILK009",
            "description": "Unsweetened almond milk 1L",
            "price": 180.00,
            "stock": 55,
            "category": "Dairy Alternatives",
            "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400"
        },
        {
            "name": "Organic Honey",
            "sku": "HONEY010",
            "description": "Pure organic honey 500g",
            "price": 350.00,
            "stock": 30,
            "category": "Pantry",
            "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784084?w=400"
        }
    ]
    
    print("🌱 Seeding products...")
    
    for product_data in products_data:
        # Generate QR code data
        product_data["qr_code_data"] = f"PRODUCT:{product_data['sku']}"
        
        existing = db.query(Product).filter(Product.sku == product_data["sku"]).first()
        if not existing:
            product = Product(**product_data)
            db.add(product)
    
    db.commit()
    print(f"✅ {len(products_data)} products seeded!")

def seed_staff(db):
    """Seed sample staff accounts"""
    staff_data = [
        {
            "email": "admin@store.com",
            "password": "admin123",
            "name": "Admin User",
            "role": "admin"
        },
        {
            "email": "staff@store.com",
            "password": "staff123",
            "name": "Gate Staff",
            "role": "staff"
        }
    ]
    
    print("🌱 Seeding staff...")
    
    for staff_info in staff_data:
        existing = db.query(Staff).filter(Staff.email == staff_info["email"]).first()
        if not existing:
            staff = Staff(
                email=staff_info["email"],
                password_hash=hash_password(staff_info["password"]),
                name=staff_info["name"],
                role=staff_info["role"]
            )
            db.add(staff)
    
    db.commit()
    print(f"✅ {len(staff_data)} staff accounts seeded!")
    print("\n📋 Staff Credentials:")
    for staff_info in staff_data:
        print(f"   Email: {staff_info['email']} | Password: {staff_info['password']}")

def main():
    """Run seed"""
    print("🚀 Starting database seed...")
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        seed_products(db)
        seed_staff(db)
        print("\n✨ Database seeded successfully!")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
