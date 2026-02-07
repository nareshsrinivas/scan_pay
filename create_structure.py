import os

BASE_DIR = "."

FOLDERS = [
    # Backend
    f"{BASE_DIR}/backend/app/models",
    f"{BASE_DIR}/backend/app/core",
    f"{BASE_DIR}/backend/app/utils",
    f"{BASE_DIR}/backend/app/tests",
    f"{BASE_DIR}/backend/app/api/auth",
    f"{BASE_DIR}/backend/app/api/products",
    f"{BASE_DIR}/backend/app/api/cart",
    f"{BASE_DIR}/backend/app/api/orders",
    f"{BASE_DIR}/backend/app/api/payments",
    f"{BASE_DIR}/backend/app/api/exit_qr",
    f"{BASE_DIR}/backend/app/api/staff",
    
    # Frontend
    f"{BASE_DIR}/frontend/public",
    f"{BASE_DIR}/frontend/src/assets/images",
    f"{BASE_DIR}/frontend/src/components/common",
    f"{BASE_DIR}/frontend/src/components/product",
    f"{BASE_DIR}/frontend/src/components/cart",
    f"{BASE_DIR}/frontend/src/components/payment",
    f"{BASE_DIR}/frontend/src/components/qr",
    f"{BASE_DIR}/frontend/src/pages",
    f"{BASE_DIR}/frontend/src/services",
    f"{BASE_DIR}/frontend/src/hooks",
    f"{BASE_DIR}/frontend/src/store",
    f"{BASE_DIR}/frontend/src/utils",
    
    # AI Service (Optional)
    f"{BASE_DIR}/ai_service/app/models",
    
    # n8n
    f"{BASE_DIR}/n8n/workflows",
    
    # Infrastructure
    f"{BASE_DIR}/infrastructure/nginx",
    f"{BASE_DIR}/infrastructure/postgres",
]

def create_structure():
    for folder in FOLDERS:
        os.makedirs(folder, exist_ok=True)
    print("✅ Folder structure created successfully!")

if __name__ == "__main__":
    create_structure()
