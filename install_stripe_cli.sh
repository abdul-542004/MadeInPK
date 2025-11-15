#!/bin/bash

# Quick installer for Stripe CLI

echo "================================================"
echo "  Installing Stripe CLI for Webhook Testing"
echo "================================================"
echo ""

# Check if already installed
if command -v stripe &> /dev/null; then
    echo "✅ Stripe CLI is already installed!"
    stripe --version
    echo ""
    echo "To get your webhook secret, run:"
    echo "  stripe login"
    echo "  stripe listen --forward-to localhost:8000/api/stripe/webhook/"
    exit 0
fi

echo "📦 Downloading Stripe CLI..."
wget -q --show-progress https://github.com/stripe/stripe-cli/releases/download/v1.19.4/stripe_1.19.4_linux_x86_64.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ Failed to download Stripe CLI"
    exit 1
fi

echo "📂 Extracting..."
tar -xzf stripe_1.19.4_linux_x86_64.tar.gz

echo "📥 Installing to /usr/local/bin..."
sudo mv stripe /usr/local/bin/

echo "🧹 Cleaning up..."
rm stripe_1.19.4_linux_x86_64.tar.gz

echo ""
echo "✅ Stripe CLI installed successfully!"
echo ""

stripe --version

echo ""
echo "================================================"
echo "  Next Steps:"
echo "================================================"
echo ""
echo "1. Login to Stripe CLI:"
echo "   stripe login"
echo ""
echo "2. Start webhook forwarding:"
echo "   stripe listen --forward-to localhost:8000/api/stripe/webhook/"
echo ""
echo "3. Copy the webhook secret (whsec_...) from the output"
echo ""
echo "4. Add it to /home/madeinpk/MadeInPK/.env:"
echo "   STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE"
echo ""
echo "5. Restart your Django server"
echo ""
echo "================================================"
