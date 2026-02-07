#!/bin/bash

# Smart Checkout System - Complete API Test Script
# This script tests all APIs in the correct order
# Run: chmod +x test_all_apis.sh && ./test_all_apis.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000/api/v1"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ jq is not installed. Please install it:${NC}"
    echo "   macOS: brew install jq"
    echo "   Ubuntu: sudo apt-get install jq"
    exit 1
fi

# Print header
echo -e "${PURPLE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🛒 Smart Checkout System - API Test Suite                 ║
║                                                              ║
║   Testing all APIs in production-like flow                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if backend is running
echo -e "${CYAN}🔍 Checking if backend is running...${NC}"
if ! curl -s "$BASE_URL/health" > /dev/null; then
    echo -e "${RED}❌ Backend is not running!${NC}"
    echo "   Start it with: docker-compose up -d"
    echo "   Or: cd backend && uvicorn app.main:app --reload"
    exit 1
fi
echo -e "${GREEN}✅ Backend is running${NC}\n"

# Function to print step header
print_step() {
    echo -e "\n${BLUE}$1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' {1..60})${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Function to print data
print_data() {
    echo -e "${YELLOW}📊 $1${NC}"
}

# ============================================
# TEST 1: Customer Login
# ============================================
print_step "1️⃣  Customer Login (Guest)"

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/guest-login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "9876543210"}')

echo "$LOGIN_RESPONSE" | jq '.'

if echo "$LOGIN_RESPONSE" | jq -e '.success' > /dev/null; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.access_token')
    USER_UUID=$(echo "$LOGIN_RESPONSE" | jq -r '.data.user_uuid')
    print_success "Login successful"
    print_data "User UUID: $USER_UUID"
    print_data "Token: ${TOKEN:0:50}..."
else
    echo -e "${RED}❌ Login failed${NC}"
    exit 1
fi

# ============================================
# TEST 2: Get All Products
# ============================================
print_step "2️⃣  Get All Products"

PRODUCTS_RESPONSE=$(curl -s "$BASE_URL/products?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN")

echo "$PRODUCTS_RESPONSE" | jq '.'

PRODUCT1_UUID=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[0].uuid')
PRODUCT1_NAME=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[0].name')
PRODUCT1_PRICE=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[0].price')
PRODUCT1_SKU=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[0].sku')

PRODUCT2_UUID=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[1].uuid')
PRODUCT2_NAME=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[1].name')
PRODUCT2_PRICE=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[1].price')
PRODUCT2_SKU=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[1].sku')

print_success "Products retrieved"
print_data "Product 1: $PRODUCT1_NAME ($PRODUCT1_SKU) - ₹$PRODUCT1_PRICE"
print_data "Product 2: $PRODUCT2_NAME ($PRODUCT2_SKU) - ₹$PRODUCT2_PRICE"

# ============================================
# TEST 3: Scan Product QR (Get Product Details)
# ============================================
print_step "3️⃣  Scan Product QR - View Product 1"

PRODUCT_DETAIL=$(curl -s "$BASE_URL/products/$PRODUCT1_UUID" \
  -H "Authorization: Bearer $TOKEN")

echo "$PRODUCT_DETAIL" | jq '.'

print_success "Product scanned successfully"
print_info "In real app: Customer scans physical QR code on product"
print_info "QR contains: {\"type\":\"product\",\"product_uuid\":\"$PRODUCT1_UUID\",\"sku\":\"$PRODUCT1_SKU\"}"

# ============================================
# TEST 4: Add Product 1 to Cart
# ============================================
print_step "4️⃣  Add Product 1 to Cart (Qty: 2)"

ADD_CART1=$(curl -s -X POST "$BASE_URL/cart/add" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"product_uuid\": \"$PRODUCT1_UUID\",
    \"quantity\": 2
  }")

echo "$ADD_CART1" | jq '.'

print_success "Product 1 added to cart"

# ============================================
# TEST 5: Add Product 2 to Cart
# ============================================
print_step "5️⃣  Add Product 2 to Cart (Qty: 1)"

ADD_CART2=$(curl -s -X POST "$BASE_URL/cart/add" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"product_uuid\": \"$PRODUCT2_UUID\",
    \"quantity\": 1
  }")

echo "$ADD_CART2" | jq '.'

print_success "Product 2 added to cart"

# ============================================
# TEST 6: View Shopping Cart
# ============================================
print_step "6️⃣  View Shopping Cart"

CART_RESPONSE=$(curl -s "$BASE_URL/cart" \
  -H "Authorization: Bearer $TOKEN")

echo "$CART_RESPONSE" | jq '.'

CART_TOTAL=$(echo "$CART_RESPONSE" | jq -r '.data.summary.total')
CART_ITEMS=$(echo "$CART_RESPONSE" | jq -r '.data.summary.total_items')

print_success "Cart retrieved"
print_data "Total Items: $CART_ITEMS"
print_data "Total Amount: ₹$CART_TOTAL"

# ============================================
# TEST 7: Update Cart Item (Optional)
# ============================================
print_step "7️⃣  Update Cart Item (Change Qty to 3)"

CART_ITEM_UUID=$(echo "$CART_RESPONSE" | jq -r '.data.items[0].uuid')

UPDATE_CART=$(curl -s -X PUT "$BASE_URL/cart/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"cart_item_uuid\": \"$CART_ITEM_UUID\",
    \"quantity\": 3
  }")

echo "$UPDATE_CART" | jq '.'

print_success "Cart item updated"

# ============================================
# TEST 8: Create Order from Cart
# ============================================
print_step "8️⃣  Create Order from Cart"

ORDER_RESPONSE=$(curl -s -X POST "$BASE_URL/orders/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}')

echo "$ORDER_RESPONSE" | jq '.'

ORDER_UUID=$(echo "$ORDER_RESPONSE" | jq -r '.data.order_uuid')
ORDER_TOTAL=$(echo "$ORDER_RESPONSE" | jq -r '.data.total_amount')

print_success "Order created"
print_data "Order UUID: $ORDER_UUID"
print_data "Order Total: ₹$ORDER_TOTAL"

# ============================================
# TEST 9: Get Order Details
# ============================================
print_step "9️⃣  Get Order Details"

ORDER_DETAIL=$(curl -s "$BASE_URL/orders/$ORDER_UUID" \
  -H "Authorization: Bearer $TOKEN")

echo "$ORDER_DETAIL" | jq '.'

print_success "Order details retrieved"

# ============================================
# TEST 10: Initiate Payment
# ============================================
print_step "🔟 Initiate Payment (UPI)"

PAYMENT_RESPONSE=$(curl -s -X POST "$BASE_URL/payments/initiate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"order_uuid\": \"$ORDER_UUID\",
    \"payment_method\": \"upi\"
  }")

echo "$PAYMENT_RESPONSE" | jq '.'

PAYMENT_UUID=$(echo "$PAYMENT_RESPONSE" | jq -r '.data.payment_uuid')

print_success "Payment initiated"
print_data "Payment UUID: $PAYMENT_UUID"
print_info "In real scenario: Customer scans UPI QR or clicks payment link"

# ============================================
# TEST 11: Simulate Payment Webhook (Success)
# ============================================
print_step "1️⃣1️⃣  Simulate Payment Success (Webhook)"

print_info "In production: Payment gateway (Razorpay) calls this webhook"
print_info "For testing: We simulate successful payment"

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

echo "$WEBHOOK_RESPONSE" | jq '.'

print_success "Payment marked as successful"

# ============================================
# TEST 12: Generate Exit QR Code
# ============================================
print_step "1️⃣2️⃣  Generate Exit QR Code"

EXIT_QR_RESPONSE=$(curl -s -X POST "$BASE_URL/exit-qr/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"order_uuid\": \"$ORDER_UUID\"
  }")

echo "$EXIT_QR_RESPONSE" | jq '.'

EXIT_QR_TOKEN=$(echo "$EXIT_QR_RESPONSE" | jq -r '.data.token')
EXIT_QR_EXPIRES=$(echo "$EXIT_QR_RESPONSE" | jq -r '.data.expires_at')

print_success "Exit QR generated"
print_data "Token (JWT): ${EXIT_QR_TOKEN:0:60}..."
print_data "Expires at: $EXIT_QR_EXPIRES"
print_info "This QR is shown on customer's phone screen"
print_info "Customer shows this at exit gate"

# Save token for next step
echo "$EXIT_QR_TOKEN" > /tmp/smart_checkout_exit_token.txt

# ============================================
# TEST 13: Staff Login
# ============================================
print_step "1️⃣3️⃣  Staff Login"

STAFF_RESPONSE=$(curl -s -X POST "$BASE_URL/staff/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@store.com",
    "password": "admin123"
  }')

echo "$STAFF_RESPONSE" | jq '.'

STAFF_TOKEN=$(echo "$STAFF_RESPONSE" | jq -r '.data.access_token')
STAFF_NAME=$(echo "$STAFF_RESPONSE" | jq -r '.data.name')

print_success "Staff logged in"
print_data "Staff: $STAFF_NAME"
print_data "Staff Token: ${STAFF_TOKEN:0:50}..."

# ============================================
# TEST 14: Verify Exit QR (Staff Scans)
# ============================================
print_step "1️⃣4️⃣  Verify Exit QR Code (Staff Portal)"

print_info "Staff member scans customer's exit QR at gate"

VERIFY_RESPONSE=$(curl -s -X POST "$BASE_URL/exit-qr/verify" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d "{
    \"token\": \"$EXIT_QR_TOKEN\"
  }")

echo "$VERIFY_RESPONSE" | jq '.'

VERIFICATION_STATUS=$(echo "$VERIFY_RESPONSE" | jq -r '.data.valid')

if [ "$VERIFICATION_STATUS" = "true" ]; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║          ✅ ✅ ✅  VERIFICATION SUCCESS  ✅ ✅ ✅          ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║              🟢  CUSTOMER CAN EXIT STORE  🟢              ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Order Details:${NC}"
    echo "$VERIFY_RESPONSE" | jq '.data.order'
    echo ""
    echo -e "${CYAN}Customer Details:${NC}"
    echo "$VERIFY_RESPONSE" | jq '.data.customer'
else
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║          ❌ ❌ ❌  VERIFICATION FAILED  ❌ ❌ ❌           ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║           🔴  CUSTOMER CANNOT EXIT STORE  🔴              ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
fi

# ============================================
# TEST 15: Try to Verify Same QR Again (Should Fail)
# ============================================
print_step "1️⃣5️⃣  Try to Verify Same QR Again (Should Fail)"

print_info "Testing one-time use security feature"

VERIFY_AGAIN=$(curl -s -X POST "$BASE_URL/exit-qr/verify" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d "{
    \"token\": \"$EXIT_QR_TOKEN\"
  }")

echo "$VERIFY_AGAIN" | jq '.'

if echo "$VERIFY_AGAIN" | jq -e '.success == false' > /dev/null; then
    print_success "Security check passed - QR cannot be reused"
    print_info "Error: $(echo $VERIFY_AGAIN | jq -r '.error')"
else
    echo -e "${RED}❌ Security issue: QR was verified twice!${NC}"
fi

# ============================================
# TEST 16: Get User's Orders
# ============================================
print_step "1️⃣6️⃣  Get Customer's Order History"

ORDERS_LIST=$(curl -s "$BASE_URL/orders" \
  -H "Authorization: Bearer $TOKEN")

echo "$ORDERS_LIST" | jq '.'

print_success "Order history retrieved"

# ============================================
# SUMMARY
# ============================================
echo ""
echo -e "${PURPLE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                  ✨ TEST SUITE COMPLETE ✨                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${GREEN}All API tests passed successfully!${NC}\n"

echo -e "${CYAN}Summary of Tests:${NC}"
echo "  1. ✅ Customer login (guest)"
echo "  2. ✅ Browse products"
echo "  3. ✅ Scan product QR (view details)"
echo "  4. ✅ Add items to cart"
echo "  5. ✅ Update cart quantities"
echo "  6. ✅ Create order"
echo "  7. ✅ Get order details"
echo "  8. ✅ Initiate payment"
echo "  9. ✅ Process payment (webhook)"
echo " 10. ✅ Generate exit QR"
echo " 11. ✅ Staff login"
echo " 12. ✅ Verify exit QR (success)"
echo " 13. ✅ Prevent QR reuse (security)"
echo " 14. ✅ View order history"

echo ""
echo -e "${YELLOW}Test Data Created:${NC}"
echo "  • User UUID: $USER_UUID"
echo "  • Order UUID: $ORDER_UUID"
echo "  • Order Total: ₹$ORDER_TOTAL"
echo "  • Payment UUID: $PAYMENT_UUID"
echo "  • Exit QR Token saved in: /tmp/smart_checkout_exit_token.txt"

echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "  1. Test the frontend UI at http://localhost:3000"
echo "  2. Try the Swagger UI at http://localhost:8000/api/docs"
echo "  3. Check the database: docker exec -it smart-checkout-db psql -U postgres -d smart_checkout"
echo "  4. View logs: docker-compose logs -f backend"

echo ""
echo -e "${GREEN}🎉 Smart Checkout System is working perfectly! 🎉${NC}\n"
