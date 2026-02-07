# Smart Checkout System - Backend

Production-grade FastAPI backend for self-checkout system.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env .env.local
# Edit .env.local with your database credentials
```

4. Initialize database:
```bash
# Create PostgreSQL database
createdb smart_checkout

# Run migrations (tables will be created automatically on first run)
python -m app.main
```

5. Seed test data:
```bash
python -m app.seed
```

6. Run server:
```bash
uvicorn app.main:app --reload --port 8000
```

## 📚 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 🔑 API Endpoints

### Authentication
- `POST /api/v1/auth/guest-login` - Guest login with phone
- `GET /api/v1/auth/profile` - Get user profile
- `POST /api/v1/auth/logout` - Logout

### Products
- `GET /api/v1/products` - List all products
- `GET /api/v1/products/{uuid}` - Get product details
- `GET /api/v1/products/qr/{qr_code}` - Scan product QR
- `POST /api/v1/products` - Create product (admin)
- `PUT /api/v1/products/{uuid}` - Update product (admin)
- `DELETE /api/v1/products/{uuid}` - Delete product (admin)

### Cart
- `POST /api/v1/cart/add` - Add to cart
- `GET /api/v1/cart` - Get cart
- `PUT /api/v1/cart/{uuid}` - Update cart item
- `DELETE /api/v1/cart/{uuid}` - Remove from cart
- `DELETE /api/v1/cart` - Clear cart

### Orders
- `POST /api/v1/orders/create` - Create order
- `GET /api/v1/orders/{uuid}` - Get order
- `GET /api/v1/orders` - Get user orders

### Payments
- `POST /api/v1/payments/initiate` - Initiate payment
- `POST /api/v1/payments/webhook` - Payment webhook
- `GET /api/v1/payments/{uuid}` - Get payment status

### Exit QR
- `POST /api/v1/exit-qr/generate` - Generate exit QR
- `POST /api/v1/exit-qr/verify` - Verify exit QR

### Staff
- `POST /api/v1/staff/login` - Staff login
- `POST /api/v1/staff/register` - Register staff

## 🗄️ Database Schema

- `users` - Customer accounts
- `products` - Product catalog
- `carts` - Shopping carts
- `orders` - Customer orders
- `order_items` - Order line items
- `payments` - Payment transactions
- `exit_qrs` - Exit QR codes
- `staff` - Staff accounts

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test guest login
curl -X POST http://localhost:8000/api/v1/auth/guest-login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"9876543210"}'

# Test get products
curl http://localhost:8000/api/v1/products
```

## 🔒 Security Features

- JWT authentication
- Password hashing (bcrypt)
- QR token expiration
- One-time use QR codes
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)

## 📝 Environment Variables

See `.env` file for all configuration options.

## 🐳 Docker

```bash
# Build
docker build -t smart-checkout-backend .

# Run
docker run -p 8000:8000 --env-file .env smart-checkout-backend
```

## 🛠️ Development

Project structure follows clean architecture:
- `models/` - Database models
- `api/` - API routes, schemas, services
- `core/` - Security, dependencies
- `utils/` - Helper functions

Each API module has:
- `routes.py` - FastAPI endpoints
- `schemas.py` - Pydantic models
- `service.py` - Business logic

## 📞 Support

For issues, check API docs at /api/docs or review error responses.
