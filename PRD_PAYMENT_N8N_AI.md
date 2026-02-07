# 📋 PRD: Payment Integration & n8n Automation

## Project: Smart Checkout System - Payment & Automation Module

---

## 1. Overview

This PRD covers the implementation of:
1. **Demo Payment System** (for showcase/testing)
2. **Razorpay Integration** (production-ready)
3. **n8n Automation Workflows** 
4. **Optional AI Service** (visual product validation)

---

## 2. Payment Integration

### 2.1 Demo Payment (Immediate - For Showcase)

**Purpose:** Allow testing without real payment gateway
**Features:**
- Simulate UPI payment flow
- Automatic success after 3 seconds
- Generate mock transaction IDs
- Test payment failures
- No actual money involved

**User Flow:**
```
Customer clicks "Pay Now" →
Shows mock UPI QR code →
Shows loading spinner (3 seconds) →
Auto-success →
Payment complete
```

**Technical Implementation:**
- Mock payment service
- Fake transaction ID generation
- Simulated webhook callback
- Toggle between demo/real mode via ENV variable

### 2.2 Razorpay Integration (Production)

**Purpose:** Real payment processing
**Features:**
- UPI payment support
- Card payments
- Net banking
- Wallets (Paytm, PhonePe, etc.)
- Payment verification
- Refund support
- Transaction history

**User Flow:**
```
Customer clicks "Pay Now" →
Backend creates Razorpay order →
Frontend shows Razorpay checkout →
Customer pays via UPI/Card →
Razorpay webhook → Backend →
Verify signature →
Update order status →
Generate exit QR
```

---

## 3. n8n Automation

### 3.1 Workflows to Implement

#### Workflow 1: Payment Success Notification
**Trigger:** Payment webhook received
**Actions:**
1. Log transaction details
2. Update order status in database
3. Generate exit QR code
4. Send confirmation SMS (optional)
5. Update inventory
6. Trigger analytics event

#### Workflow 2: Order Expiry Check
**Trigger:** Scheduled (every 5 minutes)
**Actions:**
1. Find unpaid orders > 30 minutes old
2. Mark as expired
3. Release cart items back to inventory
4. Send reminder notification (optional)

#### Workflow 3: Exit QR Expiry
**Trigger:** Scheduled (every 1 minute)
**Actions:**
1. Find exit QRs > 10 minutes old
2. Mark as expired
3. Flag for manual review if not used

#### Workflow 4: Daily Sales Report
**Trigger:** Daily at 11:59 PM
**Actions:**
1. Aggregate daily sales
2. Calculate revenue
3. Count transactions
4. Generate report
5. Send to admin email/Slack

#### Workflow 5: Low Stock Alert
**Trigger:** Product stock updated
**Actions:**
1. Check stock level
2. If < 10 units, send alert
3. Notify admin
4. Create reorder suggestion

---

## 4. AI Service (Optional)

### 4.1 Visual Product Validation

**Purpose:** Verify customer has correct items at exit
**How it works:**
1. Camera at exit captures image
2. AI detects products in image
3. Compares with order items
4. Flags mismatches

**Models:**
- YOLOv8 for object detection
- Custom trained on store products
- Real-time inference (<1 second)

**Integration:**
```
Staff scans exit QR →
Camera captures image →
Send to AI service →
AI returns detected products →
Compare with order →
If mismatch: Alert staff →
If match: Allow exit
```

---

## 5. Implementation Plan

### Phase 1: Demo Payment (Day 1)
- [ ] Create mock payment service
- [ ] Add demo mode toggle
- [ ] Frontend integration
- [ ] Test complete flow

### Phase 2: Razorpay Integration (Day 2-3)
- [ ] Sign up for Razorpay
- [ ] Get API keys
- [ ] Backend integration
- [ ] Webhook setup
- [ ] Signature verification
- [ ] Frontend Razorpay SDK
- [ ] Test with real money (₹1)

### Phase 3: n8n Setup (Day 4)
- [ ] Install n8n
- [ ] Create workflows
- [ ] Connect to database
- [ ] Test each workflow
- [ ] Set up monitoring

### Phase 4: AI Service (Day 5-7)
- [ ] Set up Python environment
- [ ] Install YOLOv8
- [ ] Create detection API
- [ ] Test with sample images
- [ ] Integrate with main system

---

## 6. Technical Specifications

### 6.1 Demo Payment API

**Endpoint:** `POST /api/v1/payments/demo/process`

**Request:**
```json
{
  "order_uuid": "...",
  "amount": 126.00,
  "simulate_failure": false
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "payment_uuid": "...",
    "transaction_id": "DEMO_TXN_1234567890",
    "status": "success",
    "amount": 126.00,
    "timestamp": "2024-02-05T10:30:00Z"
  }
}
```

### 6.2 Razorpay API

**Create Order:**
```python
razorpay_order = razorpay_client.order.create({
    "amount": amount_in_paise,
    "currency": "INR",
    "receipt": order_uuid,
    "notes": {
        "order_uuid": order_uuid,
        "user_uuid": user_uuid
    }
})
```

**Verify Webhook:**
```python
from razorpay.utility import Utility

is_valid = Utility.verify_webhook_signature(
    webhook_body,
    webhook_signature,
    webhook_secret
)
```

### 6.3 n8n Workflow Structure

**Payment Success Workflow:**
```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "parameters": {
        "path": "payment-success"
      }
    },
    {
      "name": "HTTP Request",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "parameters": {
        "url": "http://backend:8000/api/v1/exit-qr/generate",
        "method": "POST"
      }
    },
    {
      "name": "PostgreSQL",
      "type": "n8n-nodes-base.postgres",
      "position": [650, 300],
      "parameters": {
        "operation": "update",
        "table": "orders",
        "columns": "status=paid"
      }
    }
  ]
}
```

### 6.4 AI Service API

**Endpoint:** `POST /api/v1/ai/detect-products`

**Request:**
```json
{
  "image": "base64_encoded_image",
  "order_uuid": "..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "detected_products": [
      {
        "name": "Milk Tetra Pack",
        "confidence": 0.95,
        "bbox": [100, 150, 200, 300]
      }
    ],
    "match_status": "matched",
    "expected_products": ["Milk Tetra Pack", "Organic Oats"],
    "missing_products": [],
    "extra_products": []
  }
}
```

---

## 7. Environment Variables

Add to `.env`:

```env
# Payment Mode (demo or razorpay)
PAYMENT_MODE=demo

# Demo Payment Settings
DEMO_PAYMENT_DELAY_SECONDS=3
DEMO_FAILURE_RATE=0  # 0-100 (percentage)

# Razorpay (Production)
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxx

# n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook/payment-success
N8N_ENABLED=true

# AI Service
AI_SERVICE_ENABLED=false
AI_SERVICE_URL=http://localhost:8001
```

---

## 8. Success Criteria

### Demo Payment
- ✅ Payment completes in 3 seconds
- ✅ Can toggle success/failure
- ✅ Generates mock transaction ID
- ✅ Triggers webhook correctly

### Razorpay Integration
- ✅ Creates order successfully
- ✅ Customer can pay via UPI
- ✅ Webhook signature verified
- ✅ Payment status updated
- ✅ Handles failures gracefully

### n8n Automation
- ✅ All 5 workflows working
- ✅ Payments trigger automation
- ✅ Scheduled jobs run correctly
- ✅ Database updated via workflows

### AI Service
- ✅ Detects products in image
- ✅ Compares with order
- ✅ Response time < 1 second
- ✅ Accuracy > 90%

---

## 9. Testing Checklist

### Demo Payment Testing
- [ ] Successful payment flow
- [ ] Failed payment scenario
- [ ] Timeout handling
- [ ] Webhook triggering

### Razorpay Testing
- [ ] Test mode payment (₹1)
- [ ] UPI payment
- [ ] Card payment
- [ ] Failed payment
- [ ] Webhook verification
- [ ] Signature validation

### n8n Testing
- [ ] Payment success workflow
- [ ] Order expiry job
- [ ] QR expiry job
- [ ] Daily report
- [ ] Low stock alert

### AI Service Testing
- [ ] Single product detection
- [ ] Multiple products
- [ ] Missing product scenario
- [ ] Extra product scenario
- [ ] Low light conditions

---

## 10. Deployment

### Demo Mode (Immediate)
```bash
# Backend
PAYMENT_MODE=demo

# Frontend
VITE_PAYMENT_MODE=demo
```

### Production Mode (After Testing)
```bash
# Backend
PAYMENT_MODE=razorpay
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# Frontend
VITE_PAYMENT_MODE=razorpay
VITE_RAZORPAY_KEY_ID=rzp_live_xxxxx
```

---

## 11. Cost Estimation

### Razorpay
- Transaction fee: 2% + ₹3 per transaction
- For ₹100 transaction: ₹5 fee
- Monthly (100 transactions): ₹500

### n8n
- Free (self-hosted)
- Cloud: $20/month (optional)

### AI Service
- Self-hosted: Free (GPU required)
- Cloud GPU: ₹5000-10000/month

---

## 12. Documentation

Required docs:
1. Payment Integration Guide
2. n8n Workflow Setup Guide
3. AI Service Setup Guide
4. Troubleshooting Guide
5. API Documentation Updates

---

## 13. Next Steps

**Week 1:**
- Implement demo payment
- Test complete flow
- Deploy to staging

**Week 2:**
- Set up Razorpay account
- Integrate Razorpay
- Test with real payments

**Week 3:**
- Install n8n
- Create all workflows
- Test automation

**Week 4:**
- Set up AI service
- Train detection model
- Integrate with system

---

**Ready to implement? Let's start with demo payment!** 🚀
