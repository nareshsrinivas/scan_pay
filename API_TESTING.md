# 🧪 API Testing Guide

Complete guide to test all Smart Checkout System APIs using curl, Postman, or the interactive Swagger UI.

## 📍 Base URLs

- **Local Development**: `http://localhost:8000/api/v1`
- **Docker**: `http://localhost:8000/api/v1`
- **Swagger UI**: `http://localhost:8000/api/docs`

## 🔐 Authentication APIs

### 1. Guest Login

Create a guest session with phone number.

**Endpoint**: `POST /api/v1/auth/guest-login`

```bash
curl -X POST http://localhost:8000/api/v1/auth/guest-login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "9876543210"
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "user_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "phone_number": "9876543210"
  }
}
```

**Save the access_token** - you'll need it for subsequent requests.

### 2. Staff Login

Staff authentication for verification portal.

**Endpoint**: `POST /api/v1/staff/login`

```bash
curl -X POST http://localhost:8000/api/v1/staff/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@store.com",
    "password": "admin123"
  }'
```

## 📦 Product APIs

### 3. Get All Products

List all available products with pagination.

**Endpoint**: `GET /api/v1/products?page=1&limit=10`

```bash
curl http://localhost:8000/api/v1/products?page=1&limit=10 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Milk Tetra Pack",
        "sku": "MILK001",
        "price": 60.00,
        "image_url": "https://example.com/milk.jpg",
        "stock": 100,
        "description": "Fresh full cream milk"
      }
    ],
    "total": 50,
    "page": 1,
    "pages": 5
  }
}
```

### 4. Get Product by UUID

Get detailed information about a specific product.

**Endpoint**: `GET /api/v1/products/{product_uuid}`

```bash
curl http://localhost:8000/api/v1/products/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Search Products

Search products by name or SKU.

**Endpoint**: `GET /api/v1/products/search?query=milk`

```bash
curl "http://localhost:8000/api/v1/products/search?query=milk" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🛒 Cart APIs

### 6. Add Item to Cart

Add a product to the shopping cart.

**Endpoint**: `POST /api/v1/cart/add`

```bash
curl -X POST http://localhost:8000/api/v1/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "product_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "quantity": 2
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "cart_item_uuid": "789e4567-e89b-12d3-a456-426614174111",
    "product": {
      "name": "Milk Tetra Pack",
      "price": 60.00
    },
    "quantity": 2,
    "subtotal": 120.00
  }
}
```

### 7. Get Cart Items

Retrieve all items in the user's cart.

**Endpoint**: `GET /api/v1/cart`

```bash
curl http://localhost:8000/api/v1/cart \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "789e4567-e89b-12d3-a456-426614174111",
        "product": {
          "uuid": "123e4567-e89b-12d3-a456-426614174000",
          "name": "Milk Tetra Pack",
          "price": 60.00,
          "image_url": "..."
        },
        "quantity": 2,
        "subtotal": 120.00
      }
    ],
    "total_items": 2,
    "subtotal": 120.00,
    "tax": 6.00,
    "total": 126.00
  }
}
```

### 8. Update Cart Item

Change the quantity of an item in the cart.

**Endpoint**: `PUT /api/v1/cart/update`

```bash
curl -X PUT http://localhost:8000/api/v1/cart/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "cart_item_uuid": "789e4567-e89b-12d3-a456-426614174111",
    "quantity": 3
  }'
```

### 9. Remove Item from Cart

Delete an item from the cart.

**Endpoint**: `DELETE /api/v1/cart/remove/{cart_item_uuid}`

```bash
curl -X DELETE http://localhost:8000/api/v1/cart/remove/789e4567-e89b-12d3-a456-426614174111 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 10. Clear Cart

Remove all items from the cart.

**Endpoint**: `DELETE /api/v1/cart/clear`

```bash
curl -X DELETE http://localhost:8000/api/v1/cart/clear \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧾 Order APIs

### 11. Create Order

Convert cart items into an order.

**Endpoint**: `POST /api/v1/orders/create`

```bash
curl -X POST http://localhost:8000/api/v1/orders/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{}'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "order_uuid": "456e4567-e89b-12d3-a456-426614174222",
    "items": [...],
    "subtotal": 120.00,
    "tax": 6.00,
    "total_amount": 126.00,
    "status": "pending",
    "created_at": "2024-02-05T10:30:00Z"
  }
}
```

### 12. Get Order Details

Retrieve details of a specific order.

**Endpoint**: `GET /api/v1/orders/{order_uuid}`

```bash
curl http://localhost:8000/api/v1/orders/456e4567-e89b-12d3-a456-426614174222 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 13. Get User Orders

List all orders for the current user.

**Endpoint**: `GET /api/v1/orders`

```bash
curl http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 💳 Payment APIs

### 14. Initiate Payment

Start the payment process for an order.

**Endpoint**: `POST /api/v1/payments/initiate`

```bash
curl -X POST http://localhost:8000/api/v1/payments/initiate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "order_uuid": "456e4567-e89b-12d3-a456-426614174222",
    "payment_method": "upi"
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "payment_uuid": "999e4567-e89b-12d3-a456-426614174333",
    "order_uuid": "456e4567-e89b-12d3-a456-426614174222",
    "amount": 126.00,
    "payment_url": "https://razorpay.com/payment/...",
    "qr_code": "upi://pay?..."
  }
}
```

### 15. Payment Webhook (Internal)

This endpoint is called by the payment gateway (Razorpay) after payment completion.

**Endpoint**: `POST /api/v1/payments/webhook`

**Note**: This is called automatically by Razorpay, not manually.

### 16. Verify Payment

Check payment status manually.

**Endpoint**: `GET /api/v1/payments/{payment_uuid}/status`

```bash
curl http://localhost:8000/api/v1/payments/999e4567-e89b-12d3-a456-426614174333/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎫 Exit QR APIs

### 17. Generate Exit QR

Create a time-bound exit QR code after successful payment.

**Endpoint**: `POST /api/v1/exit-qr/generate`

```bash
curl -X POST http://localhost:8000/api/v1/exit-qr/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "order_uuid": "456e4567-e89b-12d3-a456-426614174222"
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "exit_qr_uuid": "111e4567-e89b-12d3-a456-426614174444",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "qr_code_url": "data:image/png;base64,iVBOR...",
    "expires_at": "2024-02-05T10:40:00Z",
    "order": {
      "uuid": "456e4567-e89b-12d3-a456-426614174222",
      "total_amount": 126.00,
      "items_count": 2
    }
  }
}
```

### 18. Verify Exit QR

Validate exit QR code at the store exit (Staff use).

**Endpoint**: `POST /api/v1/exit-qr/verify`

```bash
curl -X POST http://localhost:8000/api/v1/exit-qr/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer STAFF_TOKEN" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }'
```

**Success Response**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "order": {
      "uuid": "456e4567-e89b-12d3-a456-426614174222",
      "total_amount": 126.00,
      "payment_status": "paid",
      "items": [
        {
          "product_name": "Milk Tetra Pack",
          "quantity": 2,
          "price": 60.00
        }
      ]
    },
    "customer": {
      "phone_number": "9876543210"
    },
    "verified_at": "2024-02-05T10:35:00Z"
  }
}
```

**Error Response** (Expired/Invalid):
```json
{
  "success": false,
  "error": "QR code has expired or already been used"
}
```

## 📊 Complete Checkout Flow Test

Here's a complete sequence to test the entire checkout process:

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/guest-login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"9876543210"}' | jq -r '.data.access_token')

# 2. Get products
curl http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $TOKEN"

# 3. Add to cart (use actual product_uuid from step 2)
curl -X POST http://localhost:8000/api/v1/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"product_uuid":"PRODUCT_UUID_HERE","quantity":2}'

# 4. View cart
curl http://localhost:8000/api/v1/cart \
  -H "Authorization: Bearer $TOKEN"

# 5. Create order
ORDER_UUID=$(curl -X POST http://localhost:8000/api/v1/orders/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}' | jq -r '.data.order_uuid')

# 6. Initiate payment
curl -X POST http://localhost:8000/api/v1/payments/initiate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"order_uuid\":\"$ORDER_UUID\",\"payment_method\":\"upi\"}"

# 7. (After payment success) Generate exit QR
curl -X POST http://localhost:8000/api/v1/exit-qr/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"order_uuid\":\"$ORDER_UUID\"}"
```

## 🔧 Postman Collection

### Import into Postman

1. Create new Collection: "Smart Checkout API"
2. Add environment variables:
   - `BASE_URL`: http://localhost:8000/api/v1
   - `TOKEN`: (auto-populated from login)

3. Import all endpoints above

### Auto-populate Token

In the "Tests" tab of the login request, add:

```javascript
pm.test("Login successful", function () {
    var jsonData = pm.response.json();
    pm.environment.set("TOKEN", jsonData.data.access_token);
});
```

## 🐞 Testing Tips

1. **Check Logs**: Monitor backend logs for errors
   ```bash
   docker-compose logs -f backend
   ```

2. **Validate Responses**: All responses follow this format:
   ```json
   {
     "success": true/false,
     "data": {...} or "error": "message"
   }
   ```

3. **HTTP Status Codes**:
   - 200: Success
   - 201: Created
   - 400: Bad Request
   - 401: Unauthorized
   - 404: Not Found
   - 500: Server Error

4. **Authentication**: Always include Authorization header (except login endpoints)
   ```
   Authorization: Bearer YOUR_TOKEN_HERE
   ```

5. **UUID Format**: All UUIDs must be valid v4 format:
   ```
   550e8400-e29b-41d4-a716-446655440000
   ```

## 📝 Sample Test Data

### Products (Auto-seeded)
- Milk Tetra Pack (SKU: MILK001) - ₹60
- Organic Oats (SKU: OATS001) - ₹250
- Brown Bread (SKU: BREAD001) - ₹45
- Fresh Eggs (SKU: EGGS001) - ₹90

### Test User
- Phone: 9876543210

### Staff Account
- Email: admin@store.com
- Password: admin123

---

**Happy Testing! 🧪**
