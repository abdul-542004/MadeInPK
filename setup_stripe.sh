#!/bin/bash

# Stripe Integration Setup Script for MadeInPK
# This script helps you set up Stripe integration step by step

echo "============================================"
echo "  MadeInPK - Stripe Integration Setup"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
fi

echo -e "${BLUE}Please follow these steps:${NC}"
echo ""

# Step 1: Get Stripe keys
echo -e "${YELLOW}Step 1: Get Your Stripe API Keys${NC}"
echo "1. Go to: https://dashboard.stripe.com/test/apikeys"
echo "2. Make sure you're in TEST MODE (toggle in top right)"
echo "3. Copy your Publishable Key (starts with pk_test_...)"
echo "4. Copy your Secret Key (starts with sk_test_...)"
echo ""
read -p "Press Enter when you have your keys ready..."
echo ""

# Get publishable key
echo -e "${YELLOW}Enter your Stripe Publishable Key (pk_test_...):${NC}"
read -r STRIPE_PUBLIC_KEY
echo ""

# Get secret key
echo -e "${YELLOW}Enter your Stripe Secret Key (sk_test_...):${NC}"
read -r STRIPE_SECRET_KEY
echo ""

# Validate keys
if [[ ! $STRIPE_PUBLIC_KEY == pk_test_* ]]; then
    echo -e "${RED}Warning: Publishable key should start with 'pk_test_'${NC}"
    echo "Make sure you're in TEST MODE in Stripe Dashboard"
fi

if [[ ! $STRIPE_SECRET_KEY == sk_test_* ]]; then
    echo -e "${RED}Warning: Secret key should start with 'sk_test_'${NC}"
    echo "Make sure you're in TEST MODE in Stripe Dashboard"
fi

# Update backend .env
echo -e "${GREEN}Updating backend .env file...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/STRIPE_PUBLIC_KEY=.*/STRIPE_PUBLIC_KEY=$STRIPE_PUBLIC_KEY/" .env
    sed -i '' "s/STRIPE_SECRET_KEY=.*/STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY/" .env
else
    # Linux
    sed -i "s/STRIPE_PUBLIC_KEY=.*/STRIPE_PUBLIC_KEY=$STRIPE_PUBLIC_KEY/" .env
    sed -i "s/STRIPE_SECRET_KEY=.*/STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY/" .env
fi
echo -e "${GREEN}✓ Backend .env updated${NC}"
echo ""

# Update frontend .env
echo -e "${GREEN}Updating frontend .env file...${NC}"
FRONTEND_ENV="../MadeInPK-frontend/.env"
if [ -f "$FRONTEND_ENV" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/VITE_STRIPE_PUBLIC_KEY=.*/VITE_STRIPE_PUBLIC_KEY=$STRIPE_PUBLIC_KEY/" "$FRONTEND_ENV"
    else
        sed -i "s/VITE_STRIPE_PUBLIC_KEY=.*/VITE_STRIPE_PUBLIC_KEY=$STRIPE_PUBLIC_KEY/" "$FRONTEND_ENV"
    fi
    echo -e "${GREEN}✓ Frontend .env updated${NC}"
else
    echo -e "${YELLOW}Frontend .env not found, creating...${NC}"
    cat > "$FRONTEND_ENV" << EOF
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws
VITE_STRIPE_PUBLIC_KEY=$STRIPE_PUBLIC_KEY
EOF
    echo -e "${GREEN}✓ Frontend .env created${NC}"
fi
echo ""

# Step 2: Install Stripe CLI (optional)
echo -e "${YELLOW}Step 2: Install Stripe CLI (for webhook testing)${NC}"
echo "The Stripe CLI is needed to test webhooks locally."
echo ""
read -p "Do you want to install Stripe CLI? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v stripe &> /dev/null; then
        echo -e "${GREEN}✓ Stripe CLI already installed${NC}"
        stripe --version
    else
        echo "Installing Stripe CLI..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            brew install stripe/stripe-cli/stripe
        else
            # Linux
            wget https://github.com/stripe/stripe-cli/releases/download/v1.19.4/stripe_1.19.4_linux_x86_64.tar.gz
            tar -xvf stripe_1.19.4_linux_x86_64.tar.gz
            sudo mv stripe /usr/local/bin/
            rm stripe_1.19.4_linux_x86_64.tar.gz
        fi
        echo -e "${GREEN}✓ Stripe CLI installed${NC}"
    fi
    
    echo ""
    echo "Now logging into Stripe CLI..."
    stripe login
    echo ""
fi

# Step 3: Frontend dependencies
echo -e "${YELLOW}Step 3: Install Frontend Stripe Dependencies${NC}"
echo "Installing @stripe/stripe-js and @stripe/react-stripe-js..."
echo ""
cd ../MadeInPK-frontend
if npm list @stripe/stripe-js &> /dev/null; then
    echo -e "${GREEN}✓ Stripe packages already installed${NC}"
else
    npm install @stripe/stripe-js @stripe/react-stripe-js
    echo -e "${GREEN}✓ Stripe packages installed${NC}"
fi
cd ../MadeInPK
echo ""

# Summary
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Setup Complete! ✓${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${BLUE}Your Stripe keys have been configured:${NC}"
echo "✓ Backend .env updated"
echo "✓ Frontend .env updated"
echo "✓ Frontend packages installed"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Start the backend server:"
echo "   cd /home/madeinpk/MadeInPK"
echo "   python manage.py runserver"
echo ""
echo "2. In a new terminal, start webhook forwarding:"
echo "   stripe listen --forward-to localhost:8000/api/stripe/webhook/"
echo "   (Copy the webhook secret and update STRIPE_WEBHOOK_SECRET in .env)"
echo ""
echo "3. In another terminal, start the frontend:"
echo "   cd /home/madeinpk/MadeInPK-frontend"
echo "   npm run dev"
echo ""
echo "4. Test the integration:"
echo "   - Register/login to your app"
echo "   - Become a seller"
echo "   - Complete Stripe onboarding"
echo "   - Create a product listing"
echo "   - Test a payment"
echo ""
echo -e "${BLUE}Test Card Numbers:${NC}"
echo "Success: 4242 4242 4242 4242"
echo "Declined: 4000 0000 0000 9995"
echo "3D Secure: 4000 0025 0000 3155"
echo "Expiry: Any future date (e.g., 12/34)"
echo "CVC: Any 3 digits (e.g., 123)"
echo ""
echo -e "${BLUE}For detailed guide, see:${NC}"
echo "STRIPE_INTEGRATION_GUIDE.md"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
