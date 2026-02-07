# 🧪 Complete API Testing Guide with Examples

## 📋 Table of Contents
1. [Understanding QR Codes](#understanding-qr-codes)
2. [Setup Test Environment](#setup-test-environment)
3. [Complete Test Flow](#complete-test-flow)
4. [Testing Each API](#testing-each-api)
5. [QR Code Examples](#qr-code-examples)
6. [Common Scenarios](#common-scenarios)

---

## 🎯 Understanding QR Codes

### Two Types of QR Codes in the System

#### 1️⃣ Product QR Code (Static)
**Purpose**: Identifies the product
**Created**: When product is added to database
**Contains**: Product UUID
**Lifetime**: Permanent (doesn't expire)
**Used By**: Customer to scan and add product to cart

**Example Product QR Data**:
```json
{
  "type": "product",
  "product_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "MILK001"
}
```

**How it's created**:
```python
# In backend/app/api/products/service.py
import qrcode
import json

def create_product_qr(product_uuid, sku):
    qr_data = {
        "type": "product",
        "product_uuid": str(product_uuid),
        "sku": sku
    }
    qr = qrcode.make(json.dumps(qr_data))
    return qr  # Returns QR code image
```

#### 2️⃣ Exit QR Code (Dynamic - Time-bound)
**Purpose**: Verifies payment and allows exit
**Created**: After successful payment
**Contains**: JWT token with order details
**Lifetime**: 10 minutes (configurable)
**Used By**: Staff to verify customer has paid
**Security**: One-time use, expires automatically

**Example Exit QR Data (JWT Token)**:
```json
{
  "type": "exit",
  "order_uuid": "123e4567-e89b-12d3-a456-426614174222",
  "user_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "total_amount": 126.00,
  "payment_status": "paid",
  "expires_at": "2024-02-05T11:00:00Z",
  "created_at": "2024-02-05T10:50:00Z"
}
```

**How it's created**:
```python
# In backend/app/api/exit_qr/service.py
from jose import jwt
from datetime import datetime, timedelta
import qrcode

def generate_exit_qr(order_uuid, user_uuid, total_amount):
    # Create JWT token
    expiry = datetime.utcnow() + timedelta(minutes=10)
    token_data = {
        "type": "exit",
        "order_uuid": str(order_uuid),
        "user_uuid": str(user_uuid),
        "total_amount": float(total_amount),
        "exp": expiry.timestamp()
    }
    
    # Sign the token
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    
    # Create QR code from token
    qr = qrcode.make(token)
    return qr, token
```

---

## 🔧 Setup Test Environment

### Step 1: Start the System
```bash
cd smart-checkout-system
docker-compose up -d
```

### Step 2: Wait for Services
```bash
# Check all services are running
docker-compose ps

# Should show:
# backend - Up
# frontend - Up
# postgres - Up
# n8n - Up
```

### Step 3: Verify Backend
```bash
curl http://localhost:8000/api/v1/health

# Expected output:
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Step 4: Access API Documentation
Open: http://localhost:8000/api/docs

---

## 📝 Complete Test Flow (Step by Step)

### Scenario: Customer buys 2 items and exits store

```bash
#!/bin/bash
# Save this as test_complete_flow.sh

echo "🧪 Starting Complete API Test Flow"
echo "=================================="
echo ""

# Base URL
BASE_URL="http://localhost:8000/api/v1"

# ============================================
# STEP 1: Customer Login
# ============================================
echo "1️⃣ Customer Login (Guest)"
echo "-------------------------"

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/guest-login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "9876543210"
  }')

echo "Response: $LOGIN_RESPONSE"
echo ""

# Extract token and user_uuid
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.access_token')
USER_UUID=$(echo $LOGIN_RESPONSE | jq -r '.data.user_uuid')

echo "✅ Token: ${TOKEN:0:50}..."
echo "✅ User UUID: $USER_UUID"
echo ""

# ============================================
# STEP 2: Browse Products
# ============================================
echo "2️⃣ Get All Products"
echo "-------------------"

PRODUCTS_RESPONSE=$(curl -s "$BASE_URL/products?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN")

echo "Response: $PRODUCTS_RESPONSE" | jq '.'
echo ""

# Extract first two products
PRODUCT1_UUID=$(echo $PRODUCTS_RESPONSE | jq -r '.data.products[0].uuid')
PRODUCT1_NAME=$(echo $PRODUCTS_RESPONSE | jq -r '.data.products[0].name')
PRODUCT1_PRICE=$(echo $PRODUCTS_RESPONSE | jq -r '.data.products[0].price')

PRODUCT2_UUID=$(echo $PRODUCTS_RESPONSE | jq -r '.data.products[1].uuid')
PRODUCT2_NAME=$(echo $PRODUCTS_RESPONSE | jq -r '.data.products[1].name')
PRODUCT2_PRICE=$(echo $PRODUCTS_RESPONSE | jq -r '.data.products[1].price')

echo "✅ Product 1: $PRODUCT1_NAME (₹$PRODUCT1_PRICE) - $PRODUCT1_UUID"
echo "✅ Product 2: $PRODUCT2_NAME (₹$PRODUCT2_PRICE) - $PRODUCT2_UUID"
echo ""

# ============================================
# STEP 3: Scan Product 1 (View Details)
# ============================================
echo "3️⃣ Scan Product QR - Get Product 1 Details"
echo "-------------------------------------------"

PRODUCT1_DETAIL=$(curl -s "$BASE_URL/products/$PRODUCT1_UUID" \
  -H "Authorization: Bearer $TOKEN")

echo "Response: $PRODUCT1_DETAIL" | jq '.'
echo ""

# ============================================
# STEP 4: Add Product 1 to Cart
# ============================================
echo "4️⃣ Add Product 1 to Cart (Quantity: 2)"
echo "---------------------------------------"

ADD_CART1=$(curl -s -X POST "$BASE_URL/cart/add" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"product_uuid\": \"$PRODUCT1_UUID\",
    \"quantity\": 2
  }")

echo "Response: $ADD_CART1" | jq '.'
echo ""

# ============================================
# STEP 5: Add Product 2 to Cart
# ============================================
echo "5️⃣ Add Product 2 to Cart (Quantity: 1)"
echo "---------------------------------------"

ADD_CART2=$(curl -s -X POST "$BASE_URL/cart/add" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"product_uuid\": \"$PRODUCT2_UUID\",
    \"quantity\": 1
  }")

echo "Response: $ADD_CART2" | jq '.'
echo ""

# ============================================
# STEP 6: View Cart
# ============================================
echo "6️⃣ View Shopping Cart"
echo "---------------------"

CART_RESPONSE=$(curl -s "$BASE_URL/cart" \
  -H "Authorization: Bearer $TOKEN")

echo "Response: $CART_RESPONSE" | jq '.'

CART_TOTAL=$(echo $CART_RESPONSE | jq -r '.data.total')
echo ""
echo "✅ Cart Total: ₹$CART_TOTAL"
echo ""

# ============================================
# STEP 7: Create Order
# ============================================
echo "7️⃣ Create Order from Cart"
echo "-------------------------"

ORDER_RESPONSE=$(curl -s -X POST "$BASE_URL/orders/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}')

echo "Response: $ORDER_RESPONSE" | jq '.'

ORDER_UUID=$(echo $ORDER_RESPONSE | jq -r '.data.order_uuid')
ORDER_TOTAL=$(echo $ORDER_RESPONSE | jq -r '.data.total_amount')

echo ""
echo "✅ Order Created: $ORDER_UUID"
echo "✅ Order Total: ₹$ORDER_TOTAL"
echo ""

# ============================================
# STEP 8: Initiate Payment
# ============================================
echo "8️⃣ Initiate Payment (UPI)"
echo "-------------------------"

PAYMENT_RESPONSE=$(curl -s -X POST "$BASE_URL/payments/initiate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"order_uuid\": \"$ORDER_UUID\",
    \"payment_method\": \"upi\"
  }")

echo "Response: $PAYMENT_RESPONSE" | jq '.'

PAYMENT_UUID=$(echo $PAYMENT_RESPONSE | jq -r '.data.payment_uuid')

echo ""
echo "✅ Payment Initiated: $PAYMENT_UUID"
echo "🔗 Payment URL: $(echo $PAYMENT_RESPONSE | jq -r '.data.payment_url')"
echo ""
echo "⏸️  In real scenario, customer pays via UPI..."
echo "⏸️  Payment gateway sends webhook to backend..."
echo ""

# ============================================
# STEP 9: Simulate Payment Success
# (In production, this comes from payment gateway)
# ============================================
echo "9️⃣ Simulate Payment Webhook (Success)"
echo "--------------------------------------"

WEBHOOK_RESPONSE=$(curl -s -X POST "$BASE_URL/payments/webhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"order_uuid\": \"$ORDER_UUID\",
    \"payment_uuid\": \"$PAYMENT_UUID\",
    \"status\": \"success\",
    \"amount\": $ORDER_TOTAL,
    \"provider_reference\": \"PAY_TEST_$(date +%s)\",
    \"signature\": \"test_signature_$(date +%s)\"
  }")

echo "Response: $WEBHOOK_RESPONSE" | jq '.'
echo ""

# ============================================
# STEP 10: Generate Exit QR
# ============================================
echo "🔟 Generate Exit QR Code"
echo "------------------------"

EXIT_QR_RESPONSE=$(curl -s -X POST "$BASE_URL/exit-qr/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"order_uuid\": \"$ORDER_UUID\"
  }")

echo "Response: $EXIT_QR_RESPONSE" | jq '.'

EXIT_QR_TOKEN=$(echo $EXIT_QR_RESPONSE | jq -r '.data.token')
EXIT_QR_EXPIRES=$(echo $EXIT_QR_RESPONSE | jq -r '.data.expires_at')

echo ""
echo "✅ Exit QR Generated!"
echo "🎫 Token: ${EXIT_QR_TOKEN:0:50}..."
echo "⏰ Expires: $EXIT_QR_EXPIRES"
echo "🖼️  QR Image: Available in response as base64"
echo ""

# Save QR token for verification
echo $EXIT_QR_TOKEN > /tmp/exit_qr_token.txt

# ============================================
# STEP 11: Staff Login
# ============================================
echo "1️⃣1️⃣ Staff Login"
echo "----------------"

STAFF_RESPONSE=$(curl -s -X POST "$BASE_URL/staff/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@store.com",
    "password": "admin123"
  }')

echo "Response: $STAFF_RESPONSE" | jq '.'

STAFF_TOKEN=$(echo $STAFF_RESPONSE | jq -r '.data.access_token')

echo ""
echo "✅ Staff Logged In"
echo "🔑 Staff Token: ${STAFF_TOKEN:0:50}..."
echo ""

# ============================================
# STEP 12: Verify Exit QR (Staff)
# ============================================
echo "1️⃣2️⃣ Verify Customer Exit QR (Staff Scans)"
echo "-------------------------------------------"

VERIFY_RESPONSE=$(curl -s -X POST "$BASE_URL/exit-qr/verify" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d "{
    \"token\": \"$EXIT_QR_TOKEN\"
  }")

echo "Response: $VERIFY_RESPONSE" | jq '.'

VERIFICATION_STATUS=$(echo $VERIFY_RESPONSE | jq -r '.data.valid')

echo ""
if [ "$VERIFICATION_STATUS" = "true" ]; then
  echo "✅ ✅ ✅ VERIFICATION SUCCESS! ✅ ✅ ✅"
  echo "🟢 Customer can EXIT the store"
  echo ""
  echo "Order Details:"
  echo "-------------"
  echo $VERIFY_RESPONSE | jq '.data.order'
else
  echo "❌ VERIFICATION FAILED"
  echo "🔴 Customer CANNOT exit"
fi

echo ""
echo "=================================="
echo "✅ Complete Test Flow Finished!"
echo "=================================="
```

---

## 🎯 Testing Each API Individually

### 1. Authentication APIs

#### A. Guest Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/guest-login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "9876543210"
  }' | jq '.'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "phone_number": "9876543210"
  }
}
```

#### B. Staff Login
```bash
curl -X POST http://localhost:8000/api/v1/staff/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@store.com",
    "password": "admin123"
  }' | jq '.'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "staff_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "email": "admin@store.com",
    "name": "Admin User"
  }
}
```

---

### 2. Product APIs

#### A. Get All Products
```bash
TOKEN="YOUR_TOKEN_HERE"

curl http://localhost:8000/api/v1/products?page=1&limit=5 \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "uuid": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Milk Tetra Pack",
        "sku": "MILK001",
        "description": "Fresh full cream milk 1L",
        "price": 60.00,
        "image_url": "https://example.com/milk.jpg",
        "stock": 100,
        "qr_code_data": "{\"type\":\"product\",\"product_uuid\":\"550e8400-e29b-41d4-a716-446655440001\",\"sku\":\"MILK001\"}",
        "created_at": "2024-02-05T10:00:00Z"
      },
      {
        "uuid": "550e8400-e29b-41d4-a716-446655440002",
        "name": "Organic Oats",
        "sku": "OATS001",
        "description": "Premium quality oats 500g",
        "price": 250.00,
        "image_url": "https://example.com/oats.jpg",
        "stock": 50,
        "qr_code_data": "{\"type\":\"product\",\"product_uuid\":\"550e8400-e29b-41d4-a716-446655440002\",\"sku\":\"OATS001\"}",
        "created_at": "2024-02-05T10:00:00Z"
      }
    ],
    "total": 10,
    "page": 1,
    "limit": 5,
    "pages": 2
  }
}
```

#### B. Get Specific Product (After Scanning QR)
```bash
PRODUCT_UUID="550e8400-e29b-41d4-a716-446655440001"

curl http://localhost:8000/api/v1/products/$PRODUCT_UUID \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Milk Tetra Pack",
    "sku": "MILK001",
    "description": "Fresh full cream milk 1L",
    "price": 60.00,
    "image_url": "https://example.com/milk.jpg",
    "stock": 100,
    "category": "Dairy",
    "brand": "Amul",
    "weight": "1L",
    "qr_code_data": "{\"type\":\"product\",\"product_uuid\":\"550e8400-e29b-41d4-a716-446655440001\",\"sku\":\"MILK001\"}"
  }
}
```

---

### 3. Cart APIs

#### A. Add Item to Cart
```bash
curl -X POST http://localhost:8000/api/v1/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "product_uuid": "550e8400-e29b-41d4-a716-446655440001",
    "quantity": 2
  }' | jq '.'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "cart_item_uuid": "789e4567-e89b-12d3-a456-426614174111",
    "product": {
      "uuid": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Milk Tetra Pack",
      "price": 60.00,
      "image_url": "https://example.com/milk.jpg"
    },
    "quantity": 2,
    "subtotal": 120.00
  },
  "message": "Item added to cart"
}
```

#### B. View Cart
```bash
curl http://localhost:8000/api/v1/cart \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "789e4567-e89b-12d3-a456-426614174111",
        "product": {
          "uuid": "550e8400-e29b-41d4-a716-446655440001",
          "name": "Milk Tetra Pack",
          "price": 60.00,
          "image_url": "https://example.com/milk.jpg",
          "sku": "MILK001"
        },
        "quantity": 2,
        "subtotal": 120.00
      }
    ],
    "summary": {
      "total_items": 2,
      "unique_items": 1,
      "subtotal": 120.00,
      "tax": 6.00,
      "tax_rate": 5,
      "total": 126.00
    }
  }
}
```

#### C. Update Cart Item
```bash
CART_ITEM_UUID="789e4567-e89b-12d3-a456-426614174111"

curl -X PUT http://localhost:8000/api/v1/cart/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"cart_item_uuid\": \"$CART_ITEM_UUID\",
    \"quantity\": 3
  }" | jq '.'
```

#### D. Remove Item from Cart
```bash
curl -X DELETE http://localhost:8000/api/v1/cart/remove/$CART_ITEM_UUID \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

### 4. Order APIs

#### A. Create Order
```bash
curl -X POST http://localhost:8000/api/v1/orders/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}' | jq '.'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "order_uuid": "456e4567-e89b-12d3-a456-426614174222",
    "user_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "items": [
      {
        "product": {
          "name": "Milk Tetra Pack",
          "sku": "MILK001",
          "image_url": "https://example.com/milk.jpg"
        },
        "quantity": 2,
        "price": 60.00,
        "subtotal": 120.00
      }
    ],
    "subtotal": 120.00,
    "tax": 6.00,
    "total_amount": 126.00,
    "status": "pending",
    "created_at": "2024-02-05T10:30:00Z"
  },
  "message": "Order created successfully"
}
```

#### B. Get Order Details
```bash
ORDER_UUID="456e4567-e89b-12d3-a456-426614174222"

curl http://localhost:8000/api/v1/orders/$ORDER_UUID \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

### 5. Payment APIs

#### A. Initiate Payment
```bash
curl -X POST http://localhost:8000/api/v1/payments/initiate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "order_uuid": "456e4567-e89b-12d3-a456-426614174222",
    "payment_method": "upi"
  }' | jq '.'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "payment_uuid": "999e4567-e89b-12d3-a456-426614174333",
    "order_uuid": "456e4567-e89b-12d3-a456-426614174222",
    "amount": 126.00,
    "currency": "INR",
    "payment_method": "upi",
    "payment_url": "https://razorpay.com/payment/pay_xxxxxx",
    "qr_code": "upi://pay?pa=merchant@upi&pn=Store&am=126.00&cu=INR&tn=Order456e4567",
    "expires_at": "2024-02-05T11:30:00Z",
    "status": "pending"
  },
  "message": "Payment initiated. Please complete payment."
}
```

#### B. Check Payment Status
```bash
PAYMENT_UUID="999e4567-e89b-12d3-a456-426614174333"

curl http://localhost:8000/api/v1/payments/$PAYMENT_UUID/status \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

### 6. Exit QR APIs

#### A. Generate Exit QR (After Payment Success)
```bash
curl -X POST http://localhost:8000/api/v1/exit-qr/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "order_uuid": "456e4567-e89b-12d3-a456-426614174222"
  }' | jq '.'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "exit_qr_uuid": "111e4567-e89b-12d3-a456-426614174444",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiZXhpdCIsIm9yZGVyX3V1aWQiOiI0NTZlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQyMjIiLCJ1c2VyX3V1aWQiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0b3RhbF9hbW91bnQiOjEyNi4wLCJleHAiOjE3MDcxMzAyMDB9.xyz123abc",
    "qr_code_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "expires_at": "2024-02-05T11:00:00Z",
    "valid_until": "10 minutes",
    "order": {
      "uuid": "456e4567-e89b-12d3-a456-426614174222",
      "total_amount": 126.00,
      "items_count": 2,
      "status": "paid"
    }
  },
  "message": "Exit QR generated successfully. Valid for 10 minutes."
}
```

#### B. Verify Exit QR (Staff Portal)
```bash
# First, login as staff
STAFF_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@store.com","password":"admin123"}' | jq -r '.data.access_token')

# Then verify the exit QR
EXIT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8000/api/v1/exit-qr/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d "{
    \"token\": \"$EXIT_TOKEN\"
  }" | jq '.'
```

**Expected Response (Valid QR)**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "status": "approved",
    "message": "Customer can exit the store",
    "order": {
      "uuid": "456e4567-e89b-12d3-a456-426614174222",
      "total_amount": 126.00,
      "payment_status": "paid",
      "items": [
        {
          "product_name": "Milk Tetra Pack",
          "sku": "MILK001",
          "quantity": 2,
          "price": 60.00
        }
      ],
      "items_count": 2
    },
    "customer": {
      "phone_number": "9876543210"
    },
    "verified_at": "2024-02-05T10:55:00Z",
    "verified_by": "admin@store.com"
  }
}
```

**Expected Response (Expired/Invalid QR)**:
```json
{
  "success": false,
  "error": "QR code has expired or already been used",
  "data": {
    "valid": false,
    "status": "rejected",
    "reason": "expired"
  }
}
```

---

## 🖼️ QR Code Examples

### Product QR Code Generation

Create a script to generate product QR codes:

```python
# generate_product_qr.py
import qrcode
import json
from PIL import Image

def generate_product_qr(product_uuid, sku, product_name):
    # Create QR data
    qr_data = {
        "type": "product",
        "product_uuid": product_uuid,
        "sku": sku
    }
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save
    filename = f"product_qr_{sku}.png"
    img.save(filename)
    print(f"✅ QR Code saved: {filename}")
    print(f"📦 Product: {product_name}")
    print(f"🔑 Data: {json.dumps(qr_data)}")
    
    return filename

# Example: Generate QR for Milk
generate_product_qr(
    product_uuid="550e8400-e29b-41d4-a716-446655440001",
    sku="MILK001",
    product_name="Milk Tetra Pack"
)

# Example: Generate QR for Oats
generate_product_qr(
    product_uuid="550e8400-e29b-41d4-a716-446655440002",
    sku="OATS001",
    product_name="Organic Oats"
)
```

### Exit QR Code Visualization

```python
# visualize_exit_qr.py
import qrcode
from jose import jwt
from datetime import datetime, timedelta

def generate_exit_qr_visual(order_uuid, total_amount):
    # Create JWT token (similar to backend)
    expiry = datetime.utcnow() + timedelta(minutes=10)
    token_data = {
        "type": "exit",
        "order_uuid": order_uuid,
        "total_amount": total_amount,
        "exp": int(expiry.timestamp())
    }
    
    # Note: In production, use actual SECRET_KEY from backend
    token = jwt.encode(token_data, "demo-secret-key", algorithm="HS256")
    
    # Create QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="green", back_color="white")
    filename = f"exit_qr_{order_uuid[:8]}.png"
    img.save(filename)
    
    print(f"✅ Exit QR saved: {filename}")
    print(f"🎫 Token (first 50 chars): {token[:50]}...")
    print(f"⏰ Expires: {expiry}")
    print(f"💰 Amount: ₹{total_amount}")
    
    return filename, token

# Example
generate_exit_qr_visual(
    order_uuid="456e4567-e89b-12d3-a456-426614174222",
    total_amount=126.00
)
```

---

## 🎬 Common Test Scenarios

### Scenario 1: Happy Path (Success)
```bash
# 1. Login → 2. Add items → 3. Checkout → 4. Pay → 5. Get QR → 6. Verify → 7. Exit
# See complete flow script above
```

### Scenario 2: QR Expired
```bash
# Generate QR, wait 11 minutes, then try to verify
# Expected: Verification fails with "expired" error
```

### Scenario 3: QR Already Used
```bash
# Verify same QR twice
# Expected: Second verification fails with "already used" error
```

### Scenario 4: Invalid Payment
```bash
# Try to generate exit QR for unpaid order
# Expected: Error "Order not paid"
```

### Scenario 5: Out of Stock
```bash
# Try to add 1000 quantity when stock is 100
# Expected: Error "Insufficient stock"
```

---

## 📊 Test Data

### Pre-seeded Products

| UUID | Name | SKU | Price | Stock |
|------|------|-----|-------|-------|
| 550e8400-...-440001 | Milk Tetra Pack | MILK001 | ₹60 | 100 |
| 550e8400-...-440002 | Organic Oats | OATS001 | ₹250 | 50 |
| 550e8400-...-440003 | Brown Bread | BREAD001 | ₹45 | 75 |
| 550e8400-...-440004 | Fresh Eggs | EGGS001 | ₹90 | 60 |

### Test Credentials

**Customer:**
- Phone: 9876543210 (or any 10-digit)

**Staff:**
- Email: admin@store.com
- Password: admin123

---

## 🔍 How to Debug

### Check Logs
```bash
# Backend logs
docker-compose logs -f backend

# Database logs
docker-compose logs -f postgres
```

### Direct Database Query
```bash
# Connect to database
docker exec -it smart-checkout-db psql -U postgres -d smart_checkout

# Check products
SELECT uuid, name, sku, price FROM products;

# Check orders
SELECT uuid, total_amount, status FROM orders;

# Check exit QRs
SELECT uuid, used, expires_at FROM exit_qr;
```

---

## ✅ Success Indicators

You'll know everything works if:
- ✅ Login returns token
- ✅ Products list shows items
- ✅ Cart calculates total correctly
- ✅ Order is created from cart
- ✅ Payment can be initiated
- ✅ Exit QR is generated after payment
- ✅ Staff can verify QR successfully
- ✅ QR expires after 10 minutes
- ✅ Used QR cannot be verified again

---

**Save the complete test script and run it to test everything! 🚀**
