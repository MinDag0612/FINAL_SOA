#!/bin/bash

# Test script để test thanh toán SePay

# Get JWT token từ login
echo "🔐 Login to get JWT token..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost/auth/login" \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{
    "email": "vquan29905@gmail.com",
    "password": "12345"
  }')

echo "Login response: $LOGIN_RESPONSE"

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    exit 1
fi

echo "✅ Got token: ${TOKEN:0:50}..."
echo ""

# Create invoice
echo "📄 Creating invoice..."
INVOICE_RESPONSE=$(curl -s -X POST "http://localhost/billing/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{
    "booking_id": 14,
    "user_id": 5,
    "amount": 100000,
    "currency": "VND",
    "description": "Test booking payment"
  }')

echo "Invoice response: $INVOICE_RESPONSE"
echo ""

INVOICE_ID=$(echo $INVOICE_RESPONSE | grep -o '"invoice_id":[0-9]*' | cut -d':' -f2)

if [ -z "$INVOICE_ID" ]; then
    echo "❌ Failed to create invoice"
    exit 1
fi

echo "✅ Created invoice ID: $INVOICE_ID"
echo ""

# Create SePay payment
echo "💳 Creating SePay payment..."
PAYMENT_RESPONSE=$(curl -s -X POST "http://localhost/billing/$INVOICE_ID/sepay/create-payment" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{
    "booking_id": 14,
    "amount": 100000,
    "description": "Test payment via SePay"
  }')

echo "Payment response:"
echo "$PAYMENT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$PAYMENT_RESPONSE"
echo ""

PAYMENT_URL=$(echo $PAYMENT_RESPONSE | grep -o '"payment_url":"[^"]*' | cut -d'"' -f4)

if [ -n "$PAYMENT_URL" ] && [ "$PAYMENT_URL" != "null" ]; then
    echo "✅ Payment URL created: $PAYMENT_URL"
    echo ""
    echo "🌐 Open this URL in browser to complete payment:"
    echo "$PAYMENT_URL"
else
    echo "ℹ️  SePay disabled (payment marked as paid automatically)"
fi
