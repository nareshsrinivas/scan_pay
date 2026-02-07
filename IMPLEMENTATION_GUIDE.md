# 🚀 COMPLETE IMPLEMENTATION GUIDE
## Payment, n8n Automation & AI Service

---

## 📋 Table of Contents

1. [Payment Integration](#1-payment-integration)
2. [n8n Automation](#2-n8n-automation)
3. [AI Service](#3-ai-service)
4. [Testing Everything](#4-testing-everything)
5. [Switching to Production](#5-switching-to-production)

---

## 1. Payment Integration

### Step 1.1: Add Payment Services to Backend

**File: `backend/app/services/demo_payment.py`**
```bash
# Copy the demo_payment_service.py file to this location
cp demo_payment_service.py backend/app/services/demo_payment.py
```

**File: `backend/app/services/razorpay_service.py`**
```bash
# Copy the razorpay_service.py file to this location
cp razorpay_service.py backend/app/services/razorpay_service.py
```

### Step 1.2: Update Payment Routes

**File: `backend/app/api/payments/routes.py`**
```bash
# Replace existing routes.py with the updated version
cp payment_routes_updated.py backend/app/api/payments/routes.py
```

### Step 1.3: Update Config

**File: `backend/app/config.py`**

Add these settings:
```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Payment Mode
    PAYMENT_MODE: str = "demo"  # "demo" or "razorpay"
    
    # Demo Payment
    DEMO_PAYMENT_DELAY_SECONDS: int = 3
    DEMO_FAILURE_RATE: int = 0
    
    # Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
```

### Step 1.4: Update Environment Variables

**File: `backend/.env`**
```env
# Payment Configuration
PAYMENT_MODE=demo

# Demo Payment (for testing)
DEMO_PAYMENT_DELAY_SECONDS=3
DEMO_FAILURE_RATE=0

# Razorpay (add real keys when ready)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxx
```

### Step 1.5: Install Dependencies

```bash
cd backend
pip install razorpay --break-system-packages
```

### Step 1.6: Test Demo Payment

```bash
# Start backend
uvicorn app.main:app --reload

# Test payment initiation
curl -X POST http://localhost:8000/api/v1/payments/initiate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "order_uuid": "your-order-uuid",
    "payment_method": "upi"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "payment_uuid": "...",
    "provider": "demo",
    "transaction_id": "DEMO_TXN_...",
    "qr_code": "upi://pay?...",
    "status": "pending"
  }
}
```

### Step 1.7: Test Demo Webhook

```bash
# Simulate payment success
curl -X POST http://localhost:8000/api/v1/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "order_uuid": "your-order-uuid",
    "payment_uuid": "your-payment-uuid",
    "status": "success",
    "provider_reference": "DEMO_REF_123"
  }'
```

---

## 2. n8n Automation

### Step 2.1: Install n8n

**Option A: Using Docker (Recommended)**
```bash
# Already included in docker-compose.yml
docker-compose up -d n8n

# Access n8n at http://localhost:5678
# Login: admin / admin123
```

**Option B: Manual Install**
```bash
# Install n8n globally
npm install -g n8n

# Start n8n
n8n start

# Access at http://localhost:5678
```

### Step 2.2: Configure Database Connection

1. Open n8n: http://localhost:5678
2. Go to **Credentials** → **New**
3. Select **Postgres**
4. Enter details:
   ```
   Host: postgres (or localhost if not using Docker)
   Port: 5432
   Database: smart_checkout
   User: postgres
   Password: postgres
   ```
5. Save as "PostgreSQL account"

### Step 2.3: Import Payment Success Workflow

1. Go to **Workflows** → **Import**
2. Upload `n8n_payment_success.json`
3. Click on each node and configure:

**Webhook Node:**
- Path: `payment-success`
- Method: POST

**PostgreSQL Nodes:**
- Select "PostgreSQL account" credential
- Verify queries are correct

**HTTP Request Nodes:**
- Update URLs if needed
- Add authentication tokens

4. Click **Activate** (top right)

### Step 2.3: Create Other Workflows

#### Workflow 2: Order Expiry Check

**Create New Workflow:**
1. Add **Cron** node:
   - Schedule: `*/5 * * * *` (every 5 minutes)

2. Add **Postgres** node:
   - Operation: Execute Query
   - Query:
     ```sql
     UPDATE orders 
     SET status = 'expired' 
     WHERE status = 'pending' 
     AND created_at < NOW() - INTERVAL '30 minutes'
     ```

3. Activate workflow

#### Workflow 3: Exit QR Expiry

**Create New Workflow:**
1. Add **Cron** node:
   - Schedule: `* * * * *` (every minute)

2. Add **Postgres** node:
   - Operation: Execute Query
   - Query:
     ```sql
     UPDATE exit_qr 
     SET status = 'expired' 
     WHERE used = false 
     AND expires_at < NOW()
     ```

3. Activate workflow

#### Workflow 4: Daily Sales Report

**Create New Workflow:**
1. Add **Cron** node:
   - Schedule: `59 23 * * *` (daily at 11:59 PM)

2. Add **Postgres** node to get sales data:
   ```sql
   SELECT 
     COUNT(*) as total_orders,
     SUM(total_amount) as total_revenue,
     AVG(total_amount) as avg_order_value
   FROM orders 
   WHERE status = 'paid' 
   AND DATE(created_at) = CURRENT_DATE
   ```

3. Add **HTTP Request** node to send to admin:
   - Or add **Email** node
   - Or add **Slack** node

4. Activate workflow

### Step 2.4: Test Workflows

**Test Payment Success Workflow:**
```bash
# Send test webhook to n8n
curl -X POST http://localhost:5678/webhook/payment-success \
  -H "Content-Type: application/json" \
  -d '{
    "order_uuid": "test-order-uuid",
    "payment_uuid": "test-payment-uuid",
    "status": "success",
    "amount": 126.00
  }'
```

**Check Logs:**
- Go to **Executions** in n8n
- See if workflow ran successfully
- Check for errors

---

## 3. AI Service

### Step 3.1: Set Up AI Service

**Create Directory:**
```bash
mkdir -p ai_service/app
cd ai_service
```

**Copy AI Service Code:**
```bash
# Copy the main AI service file
cp ../ai_service_main.py app/main.py
```

**Create requirements.txt:**
```bash
cat > requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
ultralytics==8.1.0
opencv-python==4.8.1.78
pillow==10.2.0
numpy==1.24.3
python-multipart==0.0.6
EOF
```

**Create Dockerfile:**
```bash
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Download YOLOv8 model (optional - will download on first run)
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
EOF
```

### Step 3.2: Add AI Service to Docker Compose

**File: `docker-compose.yml`**

Add this service:
```yaml
  ai_service:
    build: ./ai_service
    container_name: smart-checkout-ai
    ports:
      - "8001:8001"
    networks:
      - smart-checkout-network
    environment:
      - MODEL_PATH=yolov8n.pt
    volumes:
      - ./ai_service:/app
```

### Step 3.3: Start AI Service

```bash
# Using Docker
docker-compose up -d ai_service

# Or manually
cd ai_service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Step 3.4: Test AI Service

**Health Check:**
```bash
curl http://localhost:8001/health
```

**Test Detection (Demo Mode):**
```bash
# Create a test image (or use any image)
# Convert to base64
BASE64_IMAGE=$(base64 -i test_image.jpg)

# Send detection request
curl -X POST http://localhost:8001/detect-products \
  -H "Content-Type: application/json" \
  -d "{
    \"image\": \"$BASE64_IMAGE\",
    \"order_uuid\": \"test-order\",
    \"expected_products\": [\"Milk Tetra Pack\", \"Organic Oats\"]
  }"
```

**Expected Response:**
```json
{
  "success": true,
  "detected_products": [
    {
      "name": "Milk Tetra Pack",
      "confidence": 0.92,
      "bbox": [100, 150, 200, 350]
    }
  ],
  "match_status": "matched",
  "expected_products": ["Milk Tetra Pack", "Organic Oats"],
  "missing_products": ["Organic Oats"],
  "extra_products": [],
  "confidence_score": 0.92
}
```

### Step 3.5: Integrate with Backend

**File: `backend/app/api/exit_qr/service.py`**

Add AI validation:
```python
import httpx
from app.config import get_settings

settings = get_settings()

async def verify_with_ai(order_uuid: str, image_base64: str):
    """
    Verify order items using AI detection
    """
    
    if not settings.AI_SERVICE_ENABLED:
        return {"validated": True, "method": "skipped"}
    
    # Get expected products from order
    order = db.query(Order).filter(Order.uuid == order_uuid).first()
    expected_products = [item.product.name for item in order.items]
    
    # Call AI service
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.AI_SERVICE_URL}/detect-products",
            json={
                "image": image_base64,
                "order_uuid": str(order_uuid),
                "expected_products": expected_products
            },
            timeout=10.0
        )
    
    if response.status_code == 200:
        result = response.json()
        return {
            "validated": result["match_status"] == "matched",
            "method": "ai",
            "details": result
        }
    
    return {"validated": False, "method": "ai_error"}
```

---

## 4. Testing Everything

### Complete Integration Test

```bash
#!/bin/bash

echo "🧪 Testing Complete System"

# 1. Test Demo Payment
echo "1. Testing Demo Payment..."
# ... (use test_all_apis.sh)

# 2. Test n8n Workflow
echo "2. Testing n8n Workflow..."
curl -X POST http://localhost:5678/webhook/payment-success \
  -H "Content-Type: application/json" \
  -d '{"order_uuid":"test","status":"success"}'

# 3. Test AI Service
echo "3. Testing AI Service..."
curl http://localhost:8001/health

# 4. Test Full Flow
echo "4. Testing Complete Flow..."
# Login → Add to cart → Checkout → Pay (demo) → Get QR → Verify

echo "✅ All tests complete!"
```

---

## 5. Switching to Production

### 5.1: Set Up Razorpay Account

1. Sign up at https://razorpay.com
2. Complete KYC
3. Go to **Settings** → **API Keys**
4. Generate Test Keys (for testing)
5. Generate Live Keys (for production)

### 5.2: Update Environment Variables

**For Testing (Test Mode):**
```env
PAYMENT_MODE=razorpay
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=test_secret_key_here
RAZORPAY_WEBHOOK_SECRET=whsec_test_xxxxxx
```

**For Production (Live Mode):**
```env
PAYMENT_MODE=razorpay
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=live_secret_key_here
RAZORPAY_WEBHOOK_SECRET=whsec_live_xxxxxx
```

### 5.3: Set Up Webhooks

1. Go to Razorpay Dashboard
2. Settings → Webhooks
3. Add webhook URL:
   ```
   https://your-domain.com/api/v1/payments/webhook
   ```
4. Select events:
   - payment.captured
   - payment.failed
5. Copy webhook secret to `.env`

### 5.4: Frontend Integration

**Install Razorpay SDK:**
```bash
cd frontend
npm install razorpay
```

**Update Payment Component:**
```jsx
// src/pages/Checkout.jsx
import useRazorpay from "react-razorpay";

function Checkout() {
  const Razorpay = useRazorpay();
  
  const handlePayment = async () => {
    // Get payment details from backend
    const { data } = await api.post('/payments/initiate', {
      order_uuid: orderUuid,
      payment_method: 'upi'
    });
    
    if (data.provider === 'razorpay') {
      // Use Razorpay
      const options = {
        key: data.razorpay_key_id,
        amount: data.amount,
        currency: data.currency,
        name: "Smart Checkout",
        description: `Order ${orderUuid}`,
        order_id: data.provider_payment_id,
        handler: function (response) {
          // Verify payment
          verifyPayment(response);
        }
      };
      
      const rzp = new Razorpay(options);
      rzp.open();
      
    } else {
      // Demo payment - auto success after 3 seconds
      setTimeout(() => {
        // Show success
      }, 3000);
    }
  };
  
  return (
    <button onClick={handlePayment}>
      Pay Now
    </button>
  );
}
```

### 5.5: Test with Real Money

1. Use Razorpay test mode
2. Test with ₹1 transaction
3. Use test UPI: `success@razorpay`
4. Verify webhook is called
5. Check order status updated
6. Verify exit QR generated

### 5.6: Go Live

1. Switch to live keys in `.env`
2. Restart backend
3. Test with real payment
4. Monitor transactions
5. Set up alerts

---

## 6. Monitoring & Maintenance

### Monitor n8n Workflows

```bash
# Check execution history
# Go to n8n → Executions

# Check for errors
# Fix failed workflows
```

### Monitor AI Service

```bash
# Check logs
docker logs -f smart-checkout-ai

# Monitor GPU usage (if using GPU)
nvidia-smi

# Check detection accuracy
# Review flagged mismatches
```

### Monitor Payments

```bash
# Check Razorpay Dashboard
# Review failed payments
# Process refunds if needed
```

---

## 7. Troubleshooting

### Payment Issues

**Demo payment not working:**
- Check PAYMENT_MODE=demo in .env
- Verify backend restarted after env change

**Razorpay payment fails:**
- Check API keys are correct
- Verify webhook secret
- Check webhook URL is accessible
- Review Razorpay dashboard logs

### n8n Issues

**Workflow not triggering:**
- Check webhook URL
- Verify workflow is activated
- Check execution logs

**Database connection error:**
- Verify PostgreSQL credentials
- Check database is running

### AI Service Issues

**Detection not working:**
- Check AI service is running: `curl http://localhost:8001/health`
- Verify image format is correct
- Check model is loaded

**Low accuracy:**
- Train custom model on your products
- Collect more training images
- Increase confidence threshold

---

## ✅ Final Checklist

Before going live:

- [ ] Demo payment working
- [ ] Razorpay test payment working
- [ ] Razorpay live payment working
- [ ] Webhooks configured
- [ ] n8n workflows active
- [ ] AI service running (optional)
- [ ] All tests passing
- [ ] Frontend updated with Razorpay
- [ ] Environment variables set
- [ ] SSL certificate installed
- [ ] Monitoring setup
- [ ] Backup system ready

---

**You're ready to go! 🚀**

Need help? Check the individual service documentation or API docs at `/api/docs`.
