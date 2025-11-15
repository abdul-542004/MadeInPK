# Quick Start Guide - Stripe Integration

## 🚀 Quick Setup (5 Minutes)

### Step 1: Get Your Stripe Keys (2 minutes)

1. Open [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
2. **Toggle to TEST MODE** (top right corner)
3. Copy these keys:
   - **Publishable key** (starts with `pk_test_...`)
   - **Secret key** (click "Reveal test key", starts with `sk_test_...`)

### Step 2: Configure Backend (1 minute)

Edit `/home/madeinpk/MadeInPK/.env`:

```bash
# Find these lines and replace with YOUR keys:
STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
```

### Step 3: Configure Frontend (1 minute)

Edit `/home/madeinpk/MadeInPK-frontend/.env`:

```bash
# Replace with YOUR publishable key:
VITE_STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY_HERE
```

### Step 4: Install Frontend Packages (1 minute)

```bash
cd /home/madeinpk/MadeInPK-frontend
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### Step 5: Start Everything

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

**Terminal 3 - Webhooks (Important!):**
```bash
# Install Stripe CLI if you haven't:
# Linux:
wget https://github.com/stripe/stripe-cli/releases/download/v1.19.4/stripe_1.19.4_linux_x86_64.tar.gz
tar -xvf stripe_1.19.4_linux_x86_64.tar.gz
sudo mv stripe /usr/local/bin/

# Login to Stripe CLI:
stripe login

# Forward webhooks:
stripe listen --forward-to localhost:8000/api/stripe/webhook/
```

When you run the `stripe listen` command, it will output a webhook secret like:
```
Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxxxxxxxxxx
```

**Copy that secret** and add it to your backend `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx
```

Then restart your Django server.

---

## ✅ Test Your Integration

### Test 1: Become a Seller

1. Go to `http://localhost:5173`
2. Register/Login
3. Click "Become a Seller" or similar option
4. Fill in the seller form
5. Complete Stripe onboarding using these test details:
   - **Phone:** +92 300 1234567
   - **DOB:** Any date (18+ years old)
   - **ID Number:** 000000000
   - **Bank Routing:** 110000000
   - **Bank Account:** 000123456789

### Test 2: Make a Test Payment

Use these test credit cards:

| Card Number | Scenario |
|------------|----------|
| `4242 4242 4242 4242` | ✅ Success |
| `4000 0000 0000 9995` | ❌ Declined |
| `4000 0025 0000 3155` | 🔐 3D Secure |

- **Expiry:** Any future date (12/34)
- **CVC:** Any 3 digits (123)
- **ZIP:** Any 5 digits (12345)

### Test 3: Check Stripe Dashboard

- Go to [Stripe Dashboard Payments](https://dashboard.stripe.com/test/payments)
- You should see your test payments appear
- Click on them to see:
  - Connected account (seller)
  - Application fee (2% platform commission)
  - Transfer status

---

## 🐛 Troubleshooting

### "No such API key"
- Make sure you copied the FULL key (they're very long!)
- Check for extra spaces or line breaks
- Verify you're using TEST keys (pk_test_ and sk_test_)

### Webhooks not working
- Make sure `stripe listen` is running
- Verify webhook secret in .env matches the output from `stripe listen`
- Restart Django server after adding webhook secret

### CORS errors
- Verify backend CORS settings include `http://localhost:5173`
- Restart Django server
- Clear browser cache

### "Seller has not connected Stripe account"
- Seller must complete Stripe onboarding first
- Check if `stripe_account_id` exists in database
- Try the "Connect Stripe" flow again

---

## 📚 Additional Resources

- **Full Guide:** `/home/madeinpk/MadeInPK/STRIPE_INTEGRATION_GUIDE.md`
- **Stripe Docs:** https://stripe.com/docs/connect
- **Test Cards:** https://stripe.com/docs/testing

---

## 🎯 Next Steps

1. ✅ Configure API keys
2. ✅ Install packages  
3. ✅ Start servers
4. ✅ Setup webhooks
5. ✅ Test seller onboarding
6. ✅ Test payment flow
7. 📖 Read full guide for production deployment

**Need help?** Check the full guide or Stripe documentation!
