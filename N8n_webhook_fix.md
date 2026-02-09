# 🔧 N8N WEBHOOK FIX - FINAL SOLUTION

## Problem Analysis

Your n8n workflow is correctly set up, but there are 3 issues:

1. **Webhook Mode**: Test mode vs Production mode
2. **Backend URL**: Wrong webhook URL format
3. **HTTP Method**: Must be POST, not GET

---

## ✅ SOLUTION (3 Steps)

### STEP 1: Activate Workflow in Production Mode

**In n8n UI:**

1. Open your "Payment Success Workflow"
2. Click the **webhook node** (Webhook - Payment Success)
3. You'll see two URLs:

```
Test URL:  http://localhost:5678/webhook-test/payment-success
Production URL: http://localhost:5678/webhook/payment-success
```

4. **CRITICAL**: Toggle the workflow to **ACTIVE** (switch at top right)
5. **CRITICAL**: The workflow MUST be active for production webhook to work

**Visual Check:**
- Workflow name should have a GREEN dot/checkmark when active
- Webhook node should show "Webhook is waiting for requests"

---

### STEP 2: Update Backend Webhook Configuration

Your backend is calling the webhook. We need to fix the URL and method.

#### Option A: Use Production Webhook (Recommended)

**File: `backend/app/config.py`**

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # n8n Configuration
    N8N_ENABLED: bool = True  # Enable n8n
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook/payment-success"  # Production URL
```

**File: `backend/.env`**

```env
# Enable n8n
N8N_ENABLED=true
N8N_WEBHOOK_URL=http://localhost:5678/webhook/payment-success
```

#### Option B: Use Test Webhook (For Testing Only)

If you want to use test mode:

```env
N8N_ENABLED=true
N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/payment-success
```

**Note**: Test mode requires clicking "Execute workflow" button before each test!

---

### STEP 3: Fix Backend Webhook Call

The backend needs to make a **POST request** with proper JSON data.

**File: `backend/app/api/payments/routes.py`**

**Find this function and UPDATE it:**

```python
import httpx
from datetime import datetime

async def process_demo_webhook(data: dict, db: Session):
    """Process demo payment webhook and trigger n8n"""
    
    order_uuid = data.get("order_uuid")
    payment_uuid = data.get("payment_uuid")
    status = data.get("status")
    
    if not order_uuid:
        raise HTTPException(status_code=400, detail="Missing order_uuid")
    
    # Find order
    order = db.query(Order).filter(Order.uuid == order_uuid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update order status FIRST
    if status == "success":
        order.status = "paid"
        
        # Update payment record
        if payment_uuid:
            payment = db.query(Payment).filter(Payment.uuid == payment_uuid).first()
            if payment:
                payment.status = "success"
                payment.provider_reference = data.get("provider_reference")
        
        # Commit to database BEFORE calling n8n
        db.commit()
        
        # NOW trigger n8n workflow
        if settings.N8N_ENABLED:
            try:
                print(f"🔔 Triggering n8n webhook for order {order_uuid}")
                
                # Prepare webhook payload
                webhook_payload = {
                    "order_uuid": str(order_uuid),
                    "payment_uuid": str(payment_uuid) if payment_uuid else None,
                    "status": "success",
                    "amount": float(order.total_amount),
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_uuid": str(order.user_uuid)
                }
                
                print(f"📤 Sending to n8n: {settings.N8N_WEBHOOK_URL}")
                print(f"📦 Payload: {webhook_payload}")
                
                # Make POST request to n8n
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        settings.N8N_WEBHOOK_URL,
                        json=webhook_payload,  # CRITICAL: Use json= not data=
                        headers={
                            "Content-Type": "application/json"
                        },
                        timeout=30.0  # Increase timeout
                    )
                    
                    print(f"✅ n8n response status: {response.status_code}")
                    print(f"✅ n8n response: {response.text}")
                    
                    if response.status_code == 200:
                        print(f"✅ n8n workflow triggered successfully")
                    else:
                        print(f"⚠️  n8n returned status {response.status_code}")
                        
            except httpx.TimeoutException:
                print(f"⚠️  n8n webhook timeout - workflow may still be processing")
            except httpx.RequestError as e:
                print(f"⚠️  n8n webhook error: {e}")
            except Exception as e:
                print(f"⚠️  Unexpected n8n error: {e}")
            
            # IMPORTANT: Don't fail payment if n8n fails
            # Payment already succeeded and committed to DB
    
    else:
        # Payment failed
        order.status = "payment_failed"
        
        if payment_uuid:
            payment = db.query(Payment).filter(Payment.uuid == payment_uuid).first()
            if payment:
                payment.status = "failed"
        
        db.commit()
    
    return {
        "success": True,
        "message": "Webhook processed",
        "order_status": order.status
    }
```

---

### STEP 4: Fix n8n Workflow SQL Query

**Problem in your workflow:**
```sql
-- WRONG (order_uuid doesn't exist as column)
WHERE order_uuid = '{{$json["order_uuid"]}}'

-- CORRECT (column name is 'uuid')
WHERE uuid = '{{$json["order_uuid"]}}'
```

**Update these nodes in your n8n workflow:**

**Node: "Update Order Status"**
```sql
UPDATE orders 
SET status = 'paid', updated_at = NOW() 
WHERE uuid = '{{$json["order_uuid"]}}'
```

**Node: "Update Inventory"**
```sql
UPDATE products p 
SET stock = stock - oi.quantity 
FROM order_items oi 
WHERE oi.order_uuid = '{{$json["order_uuid"]}}' 
AND p.uuid = oi.product_uuid
```

---

## 🧪 Testing the Fix

### Test 1: Verify Webhook is Registered

**Check n8n logs:**
```bash
docker logs -f n8n
```

**Should see:**
```
Webhook is waiting for requests
```

**NOT:**
```
Webhook is not registered
```

### Test 2: Test Webhook Manually

**Using curl:**
```bash
curl -X POST http://localhost:5678/webhook/payment-success \
  -H "Content-Type: application/json" \
  -d '{
    "order_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "payment_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "status": "success",
    "amount": 126.00,
    "timestamp": "2024-02-05T10:30:00Z"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Payment processed successfully"
}
```

**NOT:**
```json
{
  "code": 404,
  "message": "The requested webhook \"payment-success\" is not registered."
}
```

### Test 3: Complete Payment Flow

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/guest-login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"9876543210"}' | jq -r '.data.access_token')

# 2. Get products and add to cart
# ... (your existing flow)

# 3. Create order
ORDER_UUID=$(curl -s -X POST http://localhost:8000/api/v1/orders/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | jq -r '.data.order_uuid')

echo "Order UUID: $ORDER_UUID"

# 4. Simulate payment webhook
curl -X POST http://localhost:8000/api/v1/payments/webhook \
  -H "Content-Type: application/json" \
  -d "{
    \"order_uuid\": \"$ORDER_UUID\",
    \"payment_uuid\": \"test-payment-uuid\",
    \"status\": \"success\",
    \"provider_reference\": \"DEMO_REF_123\"
  }"

# 5. Check n8n execution
# Go to n8n UI -> Executions
# You should see a successful execution!
```

---

## 🔍 Debugging Checklist

### If webhook still shows "not registered":

✅ **Check 1: Workflow is ACTIVE**
- Go to n8n UI
- Check workflow has green indicator
- Toggle off and on again

✅ **Check 2: Webhook node settings**
```json
{
  "httpMethod": "POST",  // Must be POST
  "path": "payment-success",  // Matches your URL
  "responseMode": "responseNode"  // Important!
}
```

✅ **Check 3: Backend calling correct URL**
```bash
# Check backend logs
docker-compose logs -f backend | grep n8n

# Should see:
"Triggering n8n webhook..."
"Sending to n8n: http://localhost:5678/webhook/payment-success"
"n8n response status: 200"
```

✅ **Check 4: Network connectivity**
```bash
# From backend container, can it reach n8n?
docker exec -it smart-checkout-backend curl http://n8n:5678/webhook/payment-success
```

### If you see SQL errors in n8n:

✅ **Check table/column names**
```sql
-- Verify your schema
-- In your database:
\d orders  -- Check column names
\d order_items
\d products

-- Common issue:
-- Column is 'uuid' not 'order_uuid'
```

### If workflow executes but generates no Exit QR:

✅ **Check "Generate Exit QR" node**
```json
{
  "url": "http://backend:8000/api/v1/exit-qr/generate",  // Use container name
  "method": "POST",
  "body": {
    "order_uuid": "{{$json[\"order_uuid\"]}}"
  },
  "headers": {
    "Content-Type": "application/json"
  }
}
```

**Note**: If calling from n8n to backend, use container name `backend:8000` not `localhost:8000`

---

## 📊 Expected Flow

```
Backend Payment Webhook Handler
         ↓
    Update DB (order.status = 'paid')
         ↓
    Commit to DB
         ↓
    Call n8n webhook (POST http://localhost:5678/webhook/payment-success)
         ↓
n8n Receives Request
         ↓
    Check IF status == 'success'
         ↓ (true)
    Update Order Status (SQL)
         ↓
    Generate Exit QR (HTTP Request)
         ↓
    Update Inventory (SQL)
         ↓
    Log Analytics (SQL)
         ↓
    Respond Success
```

---

## 🎯 Quick Fix Summary

**3 Critical Changes:**

1. **Activate n8n workflow** ✅
   - Toggle to ACTIVE in n8n UI

2. **Update backend .env** ✅
   ```env
   N8N_ENABLED=true
   N8N_WEBHOOK_URL=http://localhost:5678/webhook/payment-success
   ```

3. **Fix SQL in n8n** ✅
   ```sql
   -- Change from:
   WHERE order_uuid = '{{$json["order_uuid"]}}'
   -- To:
   WHERE uuid = '{{$json["order_uuid"]}}'
   ```

---

## ✅ Success Indicators

After fix, you should see:

**In n8n logs:**
```
Received POST request for workflow "Payment Success Workflow"
Workflow executed successfully
```

**NOT:**
```
Received request for unknown webhook
The requested webhook "payment-success" is not registered
```

**In backend logs:**
```
🔔 Triggering n8n webhook for order 550e8400...
📤 Sending to n8n: http://localhost:5678/webhook/payment-success
✅ n8n response status: 200
✅ n8n workflow triggered successfully
```

**In n8n Executions tab:**
- New execution appears
- Status: Success
- All nodes executed (green checkmarks)
- Exit QR generated successfully

---

## 🚀 Final Testing Script

```bash
#!/bin/bash

echo "🧪 Testing n8n Integration"

# Test 1: Check n8n is running
echo "1. Checking n8n..."
curl -s http://localhost:5678 > /dev/null && echo "✅ n8n running" || echo "❌ n8n not running"

# Test 2: Test webhook directly
echo "2. Testing webhook..."
RESPONSE=$(curl -s -X POST http://localhost:5678/webhook/payment-success \
  -H "Content-Type: application/json" \
  -d '{
    "order_uuid": "test-order",
    "status": "success",
    "amount": 100
  }')

echo "Response: $RESPONSE"

if echo "$RESPONSE" | grep -q "success"; then
  echo "✅ Webhook responding correctly"
else
  echo "❌ Webhook error"
  echo "$RESPONSE"
fi

# Test 3: Check workflow in n8n
echo "3. Check n8n UI: http://localhost:5678"
echo "   - Go to Executions"
echo "   - Should see new execution"

echo ""
echo "✅ Testing complete!"
```

Save as `test_n8n.sh` and run: `chmod +x test_n8n.sh && ./test_n8n.sh`

---

**After these fixes, your n8n automation will work perfectly! 🎉**