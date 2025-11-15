#!/bin/bash

# Simple test script to verify Stripe integration
# Run this after completing setup

echo "🔍 Checking Stripe Integration Setup..."
echo ""

# Check backend .env
echo "1️⃣ Checking Backend Configuration..."
BACKEND_ENV="/home/madeinpk/MadeInPK/.env"

if [ ! -f "$BACKEND_ENV" ]; then
    echo "❌ Backend .env file not found!"
    exit 1
fi

PUBLIC_KEY=$(grep "STRIPE_PUBLIC_KEY=" "$BACKEND_ENV" | cut -d '=' -f2)
SECRET_KEY=$(grep "STRIPE_SECRET_KEY=" "$BACKEND_ENV" | cut -d '=' -f2)
WEBHOOK_SECRET=$(grep "STRIPE_WEBHOOK_SECRET=" "$BACKEND_ENV" | cut -d '=' -f2)

if [[ $PUBLIC_KEY == pk_test_* ]]; then
    echo "✅ Stripe Publishable Key configured"
else
    echo "❌ Stripe Publishable Key not configured or invalid"
fi

if [[ $SECRET_KEY == sk_test_* ]]; then
    echo "✅ Stripe Secret Key configured"
else
    echo "❌ Stripe Secret Key not configured or invalid"
fi

if [[ $WEBHOOK_SECRET == whsec_* ]]; then
    echo "✅ Webhook Secret configured"
else
    echo "⚠️  Webhook Secret not configured (run 'stripe listen' to get it)"
fi

echo ""

# Check frontend .env
echo "2️⃣ Checking Frontend Configuration..."
FRONTEND_ENV="/home/madeinpk/MadeInPK-frontend/.env"

if [ ! -f "$FRONTEND_ENV" ]; then
    echo "❌ Frontend .env file not found!"
    exit 1
fi

FRONTEND_KEY=$(grep "VITE_STRIPE_PUBLIC_KEY=" "$FRONTEND_ENV" | cut -d '=' -f2)

if [[ $FRONTEND_KEY == pk_test_* ]]; then
    echo "✅ Frontend Stripe Key configured"
else
    echo "❌ Frontend Stripe Key not configured or invalid"
fi

echo ""

# Check if Stripe CLI is installed
echo "3️⃣ Checking Stripe CLI..."
if command -v stripe &> /dev/null; then
    echo "✅ Stripe CLI installed"
    stripe --version
else
    echo "⚠️  Stripe CLI not installed (needed for webhook testing)"
    echo "   Install: https://stripe.com/docs/stripe-cli"
fi

echo ""

# Check if servers are running
echo "4️⃣ Checking Running Services..."

if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
    echo "✅ Backend server is running"
else
    echo "❌ Backend server is not running"
    echo "   Start with: cd /home/madeinpk/MadeInPK && python manage.py runserver"
fi

if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend server is running"
else
    echo "❌ Frontend server is not running"
    echo "   Start with: cd /home/madeinpk/MadeInPK-frontend && npm run dev"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Summary
if [[ $PUBLIC_KEY == pk_test_* ]] && [[ $SECRET_KEY == sk_test_* ]] && [[ $FRONTEND_KEY == pk_test_* ]]; then
    echo "✅ Stripe Integration is configured!"
    echo ""
    echo "Next steps:"
    echo "1. Make sure servers are running"
    echo "2. Run: stripe listen --forward-to localhost:8000/api/stripe/webhook/"
    echo "3. Copy webhook secret to backend .env"
    echo "4. Test the integration at http://localhost:5173"
    echo ""
    echo "See STRIPE_QUICKSTART.md for testing instructions"
else
    echo "⚠️  Stripe Integration needs configuration"
    echo ""
    echo "Run the setup script:"
    echo "  cd /home/madeinpk/MadeInPK"
    echo "  ./setup_stripe.sh"
    echo ""
    echo "Or see STRIPE_QUICKSTART.md for manual setup"
fi

echo ""
