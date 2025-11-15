# Stripe Integration Guide for MadeInPK

## Overview
MadeInPK uses **Stripe Connect** for marketplace payments, allowing multiple sellers to receive payments directly to their Stripe accounts while the platform collects a 2% commission.

---

## Table of Contents
1. [Getting Your Stripe API Keys](#step-1-getting-your-stripe-api-keys)
2. [Backend Configuration](#step-2-backend-configuration)
3. [Frontend Configuration](#step-3-frontend-configuration)
4. [Testing the Integration](#step-4-testing-the-integration)
5. [Webhook Setup](#step-5-webhook-setup-important)
6. [Common Issues & Solutions](#common-issues--solutions)

---

## Step 1: Getting Your Stripe API Keys

### 1.1 Access Your Stripe Dashboard
- Go to [https://dashboard.stripe.com](https://dashboard.stripe.com)
- Make sure you're in **Test Mode** (toggle in top right corner - it should show "Test mode" with a slider)

### 1.2 Get Your API Keys
1. Click on **Developers** in the left sidebar
2. Click on **API keys**
3. You'll see two keys:
   - **Publishable key** (starts with `pk_test_...`)
   - **Secret key** (starts with `sk_test_...`) - Click "Reveal test key"

### 1.3 Get Your Webhook Secret (We'll set this up later)
- For now, just note that you'll need this after creating a webhook endpoint

---

## Step 2: Backend Configuration

### 2.1 Create/Update `.env` File

In your backend directory (`/home/madeinpk/MadeInPK/`), create or update the `.env` file:

```bash
# Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=madeinpk_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (Optional for now)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password

# Stripe Configuration - REPLACE WITH YOUR ACTUAL KEYS
STRIPE_PUBLIC_KEY=pk_test_51XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
STRIPE_SECRET_KEY=sk_test_51XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Redis (for WebSockets and Celery)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**⚠️ IMPORTANT:** Replace the placeholder Stripe keys with your actual keys from Step 1.2

### 2.2 Verify Stripe Package is Installed

Your `requirements.txt` already includes `stripe==11.3.0`, which is good. If you haven't installed dependencies yet:

```bash
cd /home/madeinpk/MadeInPK
pip install -r requirements.txt
```

### 2.3 Verify Backend is Running

```bash
python manage.py runserver
```

The server should start at `http://localhost:8000`

---

## Step 3: Frontend Configuration

### 3.1 Install Stripe.js in Frontend

```bash
cd /home/madeinpk/MadeInPK-frontend
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### 3.2 Create/Update `.env` File

In your frontend directory (`/home/madeinpk/MadeInPK-frontend/`), create or update the `.env` file:

```bash
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000/api

# WebSocket Configuration
VITE_WS_BASE_URL=ws://localhost:8000/ws

# Stripe Configuration - REPLACE WITH YOUR PUBLISHABLE KEY
VITE_STRIPE_PUBLIC_KEY=pk_test_51XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**⚠️ IMPORTANT:** 
- Use the same **Publishable Key** (pk_test_...) from Step 1.2
- Never put the Secret Key in the frontend!

### 3.3 Verify Frontend is Running

```bash
npm run dev
```

The frontend should start at `http://localhost:5173`

---

## Step 4: Testing the Integration

### 4.1 Test Seller Registration Flow

1. **Register as a User:**
   - Go to `http://localhost:5173`
   - Create a new account or login

2. **Become a Seller:**
   - After logging in, find the "Become a Seller" option
   - Fill in the seller registration form
   - This should trigger the Stripe Connect account creation

3. **Complete Stripe Onboarding:**
   - You'll be redirected to Stripe to complete the onboarding
   - Use these test details:
     - **Country:** Pakistan
     - **Business Type:** Individual
     - **Phone:** Any valid format (e.g., +92 300 1234567)
     - **Date of Birth:** Any valid date (18+ years old)
     - **ID Number:** Use `000000000` (test mode accepts this)
     - **Bank Account:** Use test account numbers:
       - Routing: `110000000`
       - Account: `000123456789`

### 4.2 Test Payment Flow

**Using Stripe Test Cards:**

When making a payment, use these test card numbers:

| Card Number | Scenario |
|------------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0025 0000 3155` | Requires authentication (3D Secure) |
| `4000 0000 0000 9995` | Declined (insufficient funds) |
| `4000 0000 0000 0069` | Charge expires before capture |

**Card Details for Testing:**
- **Expiry:** Any future date (e.g., 12/34)
- **CVC:** Any 3 digits (e.g., 123)
- **ZIP:** Any 5 digits (e.g., 12345)

### 4.3 Test Scenarios

1. **Auction Payment:**
   - Create an auction listing
   - Place a winning bid
   - Complete payment checkout

2. **Fixed Price Purchase:**
   - Browse products
   - Add to cart
   - Complete checkout

3. **Multi-Seller Cart:**
   - Add products from different sellers to cart
   - Checkout and verify transfers are created

---

## Step 5: Webhook Setup (IMPORTANT)

Webhooks allow Stripe to notify your backend when payments succeed/fail.

### 5.1 Using Stripe CLI (Recommended for Local Development)

#### Install Stripe CLI

**Linux:**
```bash
wget https://github.com/stripe/stripe-cli/releases/download/v1.19.4/stripe_1.19.4_linux_x86_64.tar.gz
tar -xvf stripe_1.19.4_linux_x86_64.tar.gz
sudo mv stripe /usr/local/bin/
```

**Or use package manager:**
```bash
# Debian/Ubuntu
curl -s https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public | sudo apt-key add -
echo "deb https://packages.stripe.dev/stripe-cli-debian-local stable main" | sudo tee /etc/apt/sources.list.d/stripe.list
sudo apt update
sudo apt install stripe
```

#### Login to Stripe CLI
```bash
stripe login
```
This will open your browser for authentication.

#### Forward Webhooks to Local Server
```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook/
```

This command will output a webhook signing secret like:
```
Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxxxxxxxxxx
```

**Copy this secret** and update your backend `.env` file:
```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx
```

**Keep this terminal running** while testing payments.

### 5.2 Test Webhook Triggering

In another terminal, trigger a test payment:
```bash
stripe trigger payment_intent.succeeded
```

You should see the webhook event appear in both:
- The Stripe CLI terminal
- Your Django server logs

---

## Step 6: Verify Integration is Working

### 6.1 Backend Health Check

Test the API endpoints:

```bash
# Test health endpoint
curl http://localhost:8000/api/

# Test Stripe Connect status (replace with your auth token)
curl -H "Authorization: Token YOUR_AUTH_TOKEN" \
     http://localhost:8000/api/stripe/account-status/
```

### 6.2 Check Database

Verify Stripe IDs are being saved:

```bash
cd /home/madeinpk/MadeInPK
python manage.py shell
```

```python
from api.models import User, Payment, Order

# Check if users have Stripe account IDs
User.objects.filter(stripe_account_id__isnull=False)

# Check recent payments
Payment.objects.all().order_by('-created_at')[:5]
```

### 6.3 View Stripe Dashboard

- Go to [https://dashboard.stripe.com/test/payments](https://dashboard.stripe.com/test/payments)
- You should see your test payments appear here
- Click on any payment to see details, including:
  - Connected account (seller)
  - Application fee (platform commission)
  - Transfer status

---

## Common Issues & Solutions

### Issue 1: "No such API key"
**Solution:** 
- Make sure you copied the FULL key from Stripe (they're very long)
- Ensure there are no extra spaces or line breaks
- Verify you're using TEST keys (starting with `pk_test_` and `sk_test_`)

### Issue 2: "Invalid country: PK"
**Solution:** 
- Pakistan might not be available in test mode for all account types
- For testing purposes, you can temporarily change the country in `stripe_utils.py`:
  ```python
  # Change line ~26 in stripe_utils.py from:
  country='PK',
  # To:
  country='US',  # or 'GB' for testing
  ```

### Issue 3: Webhooks not working
**Solution:**
- Make sure Stripe CLI is running (`stripe listen --forward-to localhost:8000/api/stripe/webhook/`)
- Verify webhook secret in `.env` matches the one from Stripe CLI
- Check Django server logs for errors
- Ensure the webhook URL is correct in your API routes

### Issue 4: CORS errors in frontend
**Solution:**
- Verify `CORS_ALLOWED_ORIGINS` in backend settings includes `http://localhost:5173`
- Restart Django server after changing settings
- Clear browser cache

### Issue 5: "Seller has not connected Stripe account"
**Solution:**
- The seller must complete Stripe onboarding first
- Check the seller's `stripe_account_id` in database:
  ```python
  User.objects.get(email='seller@example.com').stripe_account_id
  ```
- If missing, the seller needs to go through the "Connect Stripe" flow again

---

## Next Steps

### For Production Deployment:

1. **Switch to Live Mode:**
   - Get live API keys from Stripe Dashboard
   - Update both backend and frontend `.env` files
   - Complete full Stripe account verification

2. **Setup Production Webhooks:**
   - In Stripe Dashboard → Developers → Webhooks
   - Add endpoint: `https://yourdomain.com/api/stripe/webhook/`
   - Select events to listen for:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `account.updated`
     - `transfer.created`
     - `transfer.updated`

3. **Business Verification:**
   - Complete your platform's Stripe account verification
   - Provide business documents if required
   - Set up payout schedule

4. **Compliance:**
   - Ensure your Terms of Service mention Stripe
   - Add privacy policy covering payment data
   - Implement proper error handling and logging

---

## Testing Checklist

- [ ] Backend `.env` has correct Stripe keys
- [ ] Frontend `.env` has correct publishable key
- [ ] Stripe CLI is installed and logged in
- [ ] Webhook forwarding is running
- [ ] User can become a seller
- [ ] Seller can complete Stripe onboarding
- [ ] Can create auction/fixed price listings
- [ ] Can complete payment for auction
- [ ] Can add items to cart and checkout
- [ ] Payment Intent is created correctly
- [ ] Webhook events are received
- [ ] Payment status updates in database
- [ ] Transfers are created for sellers
- [ ] Platform fee (2%) is deducted

---

## Useful Resources

- [Stripe Connect Documentation](https://stripe.com/docs/connect)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Stripe CLI Documentation](https://stripe.com/docs/stripe-cli)
- [Stripe Connect Onboarding](https://stripe.com/docs/connect/onboarding)

---

## Support

If you encounter issues not covered here:
1. Check Django server logs: `tail -f logs/django.log`
2. Check Stripe Dashboard for payment/transfer status
3. Check Stripe CLI output for webhook events
4. Use Django shell to inspect database records

**Happy Integration! 🚀**
