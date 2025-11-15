# 🎯 STRIPE INTEGRATION - START HERE

Hey! I've set up everything you need for Stripe integration. Here's what to do:

## 📋 What I've Created For You

1. **STRIPE_QUICKSTART.md** - Quick 5-minute setup guide
2. **STRIPE_INTEGRATION_GUIDE.md** - Detailed documentation
3. **setup_stripe.sh** - Automated setup script
4. **check_stripe_setup.sh** - Verify your setup
5. **stripeService.ts** - Frontend Stripe service
6. **.env** files - Configuration templates

## 🚀 Let's Get Started (Choose One Method)

### Method 1: Automated Setup (Easiest)
```bash
cd /home/madeinpk/MadeInPK
./setup_stripe.sh
```
This script will guide you through the entire process.

### Method 2: Manual Setup (5 Minutes)

#### Step 1: Get Your Stripe Keys
1. Go to https://dashboard.stripe.com/test/apikeys
2. Toggle to **TEST MODE** (top right)
3. Copy your **Publishable Key** (starts with `pk_test_...`)
4. Copy your **Secret Key** (starts with `sk_test_...`)

#### Step 2: Update Backend .env
Edit `/home/madeinpk/MadeInPK/.env`:
```bash
STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
```

#### Step 3: Update Frontend .env
Edit `/home/madeinpk/MadeInPK-frontend/.env`:
```bash
VITE_STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY_HERE
```

#### Step 4: Install Frontend Packages
```bash
cd /home/madeinpk/MadeInPK-frontend
npm install @stripe/stripe-js @stripe/react-stripe-js
```

#### Step 5: Install Stripe CLI (for webhooks)
```bash
# Download and install
wget https://github.com/stripe/stripe-cli/releases/download/v1.19.4/stripe_1.19.4_linux_x86_64.tar.gz
tar -xvf stripe_1.19.4_linux_x86_64.tar.gz
sudo mv stripe /usr/local/bin/

# Login
stripe login

# Start webhook forwarding
stripe listen --forward-to localhost:8000/api/stripe/webhook/
```

Copy the webhook secret from the output and add to backend `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET
```

## ✅ Verify Setup

Run this to check everything is configured:
```bash
cd /home/madeinpk/MadeInPK
./check_stripe_setup.sh
```

## 🎮 Test It Out

### Start Your Servers

**Terminal 1 - Backend:**
```bash
cd /home/madeinpk/MadeInPK
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd /home/madeinpk/MadeInPK-frontend
npm run dev
```

**Terminal 3 - Webhooks:**
```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook/
```

### Test Flow

1. **Open:** http://localhost:5173
2. **Register/Login** to your account
3. **Become a Seller** - Complete the form
4. **Stripe Onboarding** - Use test data:
   - Phone: +92 300 1234567
   - DOB: Any date (18+)
   - ID: 000000000
   - Bank Routing: 110000000
   - Account: 000123456789
5. **Create a Product** listing
6. **Test Payment** with test card: `4242 4242 4242 4242`
   - Expiry: 12/34
   - CVC: 123

## 📚 Your Backend is Already Set Up!

Your backend already has:
- ✅ Stripe models (User, Payment, SellerTransfer, etc.)
- ✅ Stripe Connect integration
- ✅ Payment processing
- ✅ Webhook handling
- ✅ Multi-seller support
- ✅ 2% platform fee system

All you need to do is:
1. Add your Stripe API keys
2. Start testing!

## 🔗 Important Links

- **Stripe Dashboard:** https://dashboard.stripe.com
- **Test Cards:** https://stripe.com/docs/testing
- **Stripe Connect Docs:** https://stripe.com/docs/connect

## 📖 Documentation

- **Quick Start:** STRIPE_QUICKSTART.md (5 min read)
- **Full Guide:** STRIPE_INTEGRATION_GUIDE.md (detailed)

## 🆘 Need Help?

### Common Issues:

**"No such API key"**
→ Make sure you copied the full key (no spaces, no line breaks)

**Webhooks not working**
→ Make sure `stripe listen` is running and webhook secret is in .env

**CORS errors**
→ Backend must include http://localhost:5173 in CORS settings (already done!)

**Can't find Stripe keys**
→ Dashboard → Developers → API Keys (make sure TEST MODE is on)

## 🎯 What You're Building

Your MadeInPK platform supports:
- 🏪 Multiple sellers (marketplace)
- 💳 Stripe Connect (sellers get paid directly)
- 🎯 Auction payments
- 🛒 Fixed-price purchases
- 🛍️ Shopping cart with multiple sellers
- 💰 Automatic 2% platform commission
- 🔄 Automatic fund transfers to sellers
- 📊 Seller earnings tracking

All of this is already coded! You just need to add your Stripe keys and test it.

---

## 🚀 Ready? Let's Go!

Run the automated setup:
```bash
cd /home/madeinpk/MadeInPK
./setup_stripe.sh
```

Or follow the manual steps above.

Then check your setup:
```bash
./check_stripe_setup.sh
```

**You got this! 💪**
