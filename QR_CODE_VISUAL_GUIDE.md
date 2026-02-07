# 🎯 QR Code Testing Guide - Visual Examples

## Understanding the Two Types of QR Codes

### 📦 Type 1: Product QR Code

**Purpose**: Identifies products for scanning and adding to cart

**What it contains**:
```json
{
  "type": "product",
  "product_uuid": "550e8400-e29b-41d4-a716-446655440001",
  "sku": "MILK001"
}
```

**Visual Representation**:
```
┌─────────────────────────────┐
│  ████████████████████████   │
│  ██░░░░██░░░░░░░░██░░░░██   │
│  ██░██░██░██████░██░██░██   │  Product QR Code
│  ██░██░██░██████░██░██░██   │  (Static - Never Expires)
│  ██░██░██░██████░██░██░██   │
│  ██░░░░██░░░░░░░░██░░░░██   │  Scan this to:
│  ████████████████████████   │  → Get product details
│                             │  → See price, image
│  MILK001                    │  → Add to cart
│  Milk Tetra Pack            │
│  ₹60.00                     │
└─────────────────────────────┘
```

**Lifetime**: ∞ (Permanent)
**Security**: None needed (public data)
**Printed on**: Product packaging or shelf labels

---

### 🎫 Type 2: Exit QR Code

**Purpose**: Verifies payment and allows customer to exit store

**What it contains** (JWT Token):
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiZXhpdCIsIm9yZGVyX3V1aWQiOiI0NTZlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQyMjIiLCJ1c2VyX3V1aWQiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0b3RhbF9hbW91bnQiOjEyNi4wLCJleHAiOjE3MDcxMzAyMDB9.xyz123abc
```

**Decoded JWT Payload**:
```json
{
  "type": "exit",
  "order_uuid": "456e4567-e89b-12d3-a456-426614174222",
  "user_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "total_amount": 126.00,
  "payment_status": "paid",
  "exp": 1707130200
}
```

**Visual Representation**:
```
┌─────────────────────────────┐
│                             │
│  ████████████████████████   │
│  ██░░░░██░░░░░░░░██░░░░██   │  Exit QR Code
│  ██░██░██░██████░██░██░██   │  (Dynamic - Expires in 10 min)
│  ██░██░██░██████░██░██░██   │
│  ██░██░██░██████░██░██░██   │  Staff scans to verify:
│  ██░░░░██░░░░░░░░██░░░░██   │  ✓ Payment successful
│  ████████████████████████   │  ✓ Amount matches
│                             │  ✓ Not expired
│  ✅ PAYMENT VERIFIED         │  ✓ Not used before
│  Order: #...174222          │
│  Amount: ₹126.00            │
│  Expires: 10:40 AM          │
│  🟢 VALID - ALLOW EXIT      │
│                             │
└─────────────────────────────┘
```

**Lifetime**: 10 minutes
**Security**: 
- JWT signed with secret key
- Contains expiration timestamp
- One-time use (marked as used after scan)
- Tamper-proof (signature verification)

**Displayed on**: Customer's phone screen (not printed)

---

## 🔄 Complete Flow with QR Codes

### Customer Journey

```
1. ENTER STORE
   └─> Walk in

2. PICK PRODUCT (e.g., Milk)
   └─> Take product from shelf

3. SCAN PRODUCT QR
   ┌──────────────────┐
   │  Product Label   │
   │  ┌────────────┐  │
   │  │ [QR CODE]  │  │ <── Customer scans this with phone
   │  └────────────┘  │
   │  Milk Tetra Pack │
   │  SKU: MILK001    │
   │  ₹60.00          │
   └──────────────────┘
   
   Phone Camera → Reads QR → Extracts: {"product_uuid":"...", "sku":"MILK001"}
   App → Sends to API: GET /products/550e8400-...-440001
   API → Returns: Product details, image, price, stock
   
4. VIEW PRODUCT DETAILS
   ┌──────────────────────┐
   │ 📱 PHONE SCREEN      │
   │ ┌──────────────────┐ │
   │ │  [Product Image] │ │
   │ │                  │ │
   │ │ Milk Tetra Pack  │ │
   │ │ ₹60.00           │ │
   │ │                  │ │
   │ │ Fresh full cream │ │
   │ │ milk - 1 Liter   │ │
   │ │                  │ │
   │ │ Qty: [1] [+][-]  │ │
   │ │                  │ │
   │ │ [Add to Cart]    │ │
   │ └──────────────────┘ │
   └──────────────────────┘

5. ADD TO CART
   App → POST /cart/add
   API → Creates cart item
   Cart → Shows 1 item, ₹60.00

6. REPEAT for more products...

7. VIEW CART
   ┌──────────────────────┐
   │ 📱 SHOPPING CART     │
   │ ┌──────────────────┐ │
   │ │ Milk - Qty: 2    │ │
   │ │ ₹120.00          │ │
   │ │                  │ │
   │ │ Oats - Qty: 1    │ │
   │ │ ₹250.00          │ │
   │ │ ─────────────────│ │
   │ │ Subtotal: ₹370   │ │
   │ │ Tax (5%): ₹18.50 │ │
   │ │ Total: ₹388.50   │ │
   │ │                  │ │
   │ │ [Proceed to Pay] │ │
   │ └──────────────────┘ │
   └──────────────────────┘

8. CREATE ORDER
   App → POST /orders/create
   API → Creates order from cart items
   Order → UUID: 456e4567-..., Total: ₹388.50, Status: pending

9. PAY VIA UPI
   App → POST /payments/initiate
   API → Generates UPI payment link
   
   ┌──────────────────────┐
   │ 📱 PAYMENT           │
   │ ┌──────────────────┐ │
   │ │ [UPI QR CODE]    │ │ <── Customer scans with payment app
   │ │                  │ │     (Google Pay, PhonePe, etc.)
   │ │ Pay ₹388.50      │ │
   │ │ to Store Name    │ │
   │ │                  │ │
   │ │ [Pay Now]        │ │
   │ └──────────────────┘ │
   └──────────────────────┘
   
   Customer → Opens Google Pay/PhonePe
   Customer → Scans UPI QR code
   Customer → Enters PIN and pays
   Payment Gateway → Sends webhook to backend
   Backend → Updates order status to "paid"

10. PAYMENT SUCCESS
    Backend → POST /exit-qr/generate
    Backend → Creates JWT token with order details
    Backend → Generates Exit QR code
    
    ┌──────────────────────┐
    │ 📱 PAYMENT SUCCESS   │
    │ ┌──────────────────┐ │
    │ │  ✅ PAID         │ │
    │ │                  │ │
    │ │ Amount: ₹388.50  │ │
    │ │ Order: #...222   │ │
    │ │                  │ │
    │ │ [EXIT QR CODE]   │ │ <── Show this at gate
    │ │ ████████████████ │ │
    │ │ ████████████████ │ │
    │ │ ████████████████ │ │
    │ │                  │ │
    │ │ Valid for 10 min │ │
    │ │ Expires: 10:40   │ │
    │ └──────────────────┘ │
    └──────────────────────┘

11. GO TO EXIT
    Customer → Walks to store exit
    Customer → Shows phone screen to staff

12. STAFF SCANS EXIT QR
    ┌──────────────────────┐
    │ 💻 STAFF TABLET      │
    │ ┌──────────────────┐ │
    │ │ Scan Exit QR     │ │
    │ │ ─────────────────│ │
    │ │ [Camera View]    │ │ <── Staff scans customer's QR
    │ │                  │ │
    │ │ Scanning...      │ │
    │ └──────────────────┘ │
    └──────────────────────┘
    
    Staff App → Reads QR code (JWT token)
    Staff App → POST /exit-qr/verify
    Backend → Decodes JWT
    Backend → Verifies:
              ✓ Token signature valid
              ✓ Not expired (within 10 min)
              ✓ Order is paid
              ✓ QR not used before
    Backend → Marks QR as used
    Backend → Returns order details

13. VERIFICATION RESULT
    
    SUCCESS (Green Screen):
    ┌──────────────────────┐
    │ 💻 STAFF TABLET      │
    │ ┌──────────────────┐ │
    │ │ 🟢🟢🟢🟢🟢🟢🟢🟢🟢│ │
    │ │                  │ │
    │ │ ✅ VERIFIED       │ │
    │ │                  │ │
    │ │ Order: #...222   │ │
    │ │ Amount: ₹388.50  │ │
    │ │ Items: 3         │ │
    │ │ Customer: 987654 │ │
    │ │                  │ │
    │ │ ALLOW EXIT ✓     │ │
    │ │                  │ │
    │ └──────────────────┘ │
    └──────────────────────┘
    
    FAILURE (Red Screen):
    ┌──────────────────────┐
    │ 💻 STAFF TABLET      │
    │ ┌──────────────────┐ │
    │ │ 🔴🔴🔴🔴🔴🔴🔴🔴🔴│ │
    │ │                  │ │
    │ │ ❌ INVALID        │ │
    │ │                  │ │
    │ │ Reason:          │ │
    │ │ QR code expired  │ │
    │ │                  │ │
    │ │ DO NOT ALLOW     │ │
    │ │                  │ │
    │ └──────────────────┘ │
    └──────────────────────┘

14. EXIT STORE
    Staff → Opens gate/door
    Customer → Exits with products
```

---

## 🧪 How to Test

### Test Product QR Scanning

**Option 1: Using Frontend App**
```bash
1. Start system: docker-compose up -d
2. Open browser: http://localhost:3000
3. Login: phone = 9876543210
4. Go to "Scan Product" page
5. Allow camera access
6. Create a test QR code:
   - Open: https://www.qr-code-generator.com/
   - Enter this text:
     {"type":"product","product_uuid":"550e8400-e29b-41d4-a716-446655440001","sku":"MILK001"}
   - Generate QR code
   - Display on another device or print
7. Scan the QR code with the app
8. Should fetch and display product details!
```

**Option 2: Using curl (Backend only)**
```bash
# Simulate what happens when QR is scanned
TOKEN="your_login_token"
PRODUCT_UUID="550e8400-e29b-41d4-a716-446655440001"

curl http://localhost:8000/api/v1/products/$PRODUCT_UUID \
  -H "Authorization: Bearer $TOKEN"
```

### Test Exit QR Verification

**Complete Test Flow:**
```bash
# Run the test_complete_flow.sh script provided earlier
chmod +x test_complete_flow.sh
./test_complete_flow.sh

# This will:
# 1. Login customer
# 2. Add products to cart
# 3. Create order
# 4. Simulate payment
# 5. Generate exit QR
# 6. Login staff
# 7. Verify exit QR
```

**Manual Test:**
```bash
# 1. Complete purchase flow (follow steps 1-10 above)
# 2. Get the exit QR token from response
# 3. Staff login
STAFF_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@store.com","password":"admin123"}' | jq -r '.data.access_token')

# 4. Verify the token
curl -X POST http://localhost:8000/api/v1/exit-qr/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{"token":"paste_exit_qr_token_here"}' | jq '.'
```

---

## 📊 QR Code Comparison

| Feature | Product QR | Exit QR |
|---------|-----------|---------|
| **Content** | JSON with UUID & SKU | Signed JWT token |
| **Lifetime** | Permanent | 10 minutes |
| **Security** | None (public) | Cryptographically signed |
| **Generated** | Once per product | After each payment |
| **Printed** | Yes (on labels) | No (shown on screen) |
| **Scanned by** | Customer (phone) | Staff (tablet/scanner) |
| **Purpose** | Add to cart | Verify payment & exit |
| **Reusable** | Yes, unlimited | No, one-time only |

---

## 🔐 Security Features

### Product QR Security
- ✅ No security needed (public data)
- ✅ UUID prevents guessing product IDs
- ✅ Backend validates product exists
- ✅ Backend checks stock availability

### Exit QR Security
- ✅ **JWT Signature**: Tamper-proof, cryptographically signed
- ✅ **Expiration**: Auto-expires after 10 minutes
- ✅ **One-time Use**: Marked as used after scan
- ✅ **Order Validation**: Verifies payment status
- ✅ **Amount Verification**: Ensures correct amount paid
- ✅ **Timestamp Check**: Server-side time validation

**Example Exit QR Validation:**
```python
def verify_exit_qr(token):
    try:
        # 1. Decode and verify signature
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # 2. Check expiration
        if datetime.now() > datetime.fromtimestamp(payload['exp']):
            return {"valid": False, "reason": "expired"}
        
        # 3. Check if already used
        qr_record = db.query(ExitQR).filter_by(token=token).first()
        if qr_record.used:
            return {"valid": False, "reason": "already_used"}
        
        # 4. Check order is paid
        order = db.query(Order).filter_by(uuid=payload['order_uuid']).first()
        if order.status != "paid":
            return {"valid": False, "reason": "order_not_paid"}
        
        # 5. Mark as used
        qr_record.used = True
        db.commit()
        
        # 6. Return success
        return {
            "valid": True,
            "order": order.to_dict(),
            "customer": order.user.to_dict()
        }
        
    except jwt.ExpiredSignatureError:
        return {"valid": False, "reason": "token_expired"}
    except jwt.JWTError:
        return {"valid": False, "reason": "invalid_token"}
```

---

## 🎨 Customization

### Custom Product QR Design

You can customize product QR labels:
```python
def create_branded_qr(product):
    # Add company logo in center
    # Add brand colors
    # Add product image
    # Add barcode alongside QR
    
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(json.dumps(product_data))
    qr.make()
    
    img = qr.make_image(fill_color="#13ec5b", back_color="white")
    
    # Overlay logo
    logo = Image.open("company_logo.png")
    # ... add logo to center ...
    
    return img
```

### Custom Exit QR Display

Customize the exit QR screen:
- Add store branding
- Show order summary
- Add countdown timer
- Animate QR code
- Add success confetti

---

**Ready to test? Use the complete test script or Swagger UI at http://localhost:8000/api/docs! 🚀**
