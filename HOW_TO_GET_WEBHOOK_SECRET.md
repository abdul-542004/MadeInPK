# 🎯 How to Get Your Webhook Secret

## The webhook secret is NOT in the Stripe Dashboard!

You need to create it using the **Stripe CLI**. Here's how:

---

## Option 1: Using Stripe CLI (Recommended for Local Development)

### Step 1: Install Stripe CLI

```bash
# Download Stripe CLI
wget https://github.com/stripe/stripe-cli/releases/download/v1.19.4/stripe_1.19.4_linux_x86_64.tar.gz

# Extract
tar -xvf stripe_1.19.4_linux_x86_64.tar.gz

# Move to /usr/local/bin
sudo mv stripe /usr/local/bin/

# Clean up
rm stripe_1.19.4_linux_x86_64.tar.gz
```

### Step 2: Login to Stripe CLI

```bash
stripe login
```

This will open your browser. Click "Allow access" to authenticate.

### Step 3: Start Webhook Forwarding

```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook/
```

**This command will output something like:**
```
> Ready! You are using Stripe API Version [2024-11-20.acacia]. Your webhook signing secret is whsec_1234567890abcdefghijklmnopqrstuvwxyz (^C to quit)
```

### Step 4: Copy the Webhook Secret

Copy the secret (starts with `whsec_...`) and update your backend `.env`:

```bash
STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdefghijklmnopqrstuvwxyz
```

### Step 5: Restart Django Server

After updating `.env`, restart your Django server:
```bash
# Stop the server (Ctrl+C)
# Then restart:
python manage.py runserver
```

### ⚠️ Important: Keep `stripe listen` Running!

While testing locally, you need to keep the `stripe listen` command running in a separate terminal. This forwards webhook events from Stripe to your local server.

---

## Option 2: Create Webhook in Stripe Dashboard (For Production Only)

This is for when you deploy to production with a public URL:

1. Go to https://dashboard.stripe.com/test/webhooks
2. Click **"Add endpoint"**
3. Enter your endpoint URL: `https://yourdomain.com/api/stripe/webhook/`
4. Select events to listen for:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `account.updated`
   - `transfer.created`
   - `transfer.updated`
5. Click **"Add endpoint"**
6. Copy the **"Signing secret"** (whsec_...)
7. Add to production `.env`

**Note:** This won't work for local development since Stripe can't reach `localhost`.

---

## Quick Install Script

Run this to install Stripe CLI automatically:

```bash
cd /home/madeinpk/MadeInPK
bash << 'EOF'
echo "📦 Installing Stripe CLI..."
wget -q https://github.com/stripe/stripe-cli/releases/download/v1.19.4/stripe_1.19.4_linux_x86_64.tar.gz
tar -xzf stripe_1.19.4_linux_x86_64.tar.gz
sudo mv stripe /usr/local/bin/
rm stripe_1.19.4_linux_x86_64.tar.gz
echo "✅ Stripe CLI installed!"
echo ""
echo "Now run these commands:"
echo "1. stripe login"
echo "2. stripe listen --forward-to localhost:8000/api/stripe/webhook/"
EOF
```

---

## Testing Without Webhooks (Temporary)

If you want to test payments without setting up webhooks right now, you can:

1. **Update backend `.env` with a dummy webhook secret:**
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_dummy_for_testing
   ```

2. **Restart Django server**

3. **Test payments** - they will work, but:
   - Order status won't auto-update after payment
   - You'll need to manually check Stripe Dashboard
   - Sellers won't get automatic notifications

**For full functionality, you need webhooks!**

---

## Summary

**For Local Development (Your Current Setup):**

```bash
# Terminal 1 - Backend
cd /home/madeinpk/MadeInPK
python manage.py runserver

# Terminal 2 - Frontend  
cd /home/madeinpk/MadeInPK-frontend
npm start  # or npm run dev

# Terminal 3 - Webhooks (REQUIRED for full functionality)
stripe login
stripe listen --forward-to localhost:8000/api/stripe/webhook/
# Copy the whsec_... secret and add to backend .env
# Then restart backend server
```

**That's it!** The webhook secret comes from the `stripe listen` command, not the dashboard.
