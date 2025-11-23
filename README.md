# MadeInPK - Backend

**MadeInPK** is a dedicated e-commerce platform that empowers Pakistani artisans, manufacturers, and small businesses by combining fixed-price selling with real-time auctions. Unlike traditional platforms that only offer fixed prices, MadeInPK enables competitive bidding, ensuring sellers can maximize profits while buyers enjoy fair, demand-driven prices.

## 🚀 Tech Stack

- **Framework:** Django 5.2.7 + Django REST Framework
- **Database:** PostgreSQL
- **Cache/Message Broker:** Redis
- **WebSockets:** Django Channels + Daphne (ASGI)
- **Task Queue:** Celery + Celery Beat
- **Payments:** Stripe (with Connect for multi-seller)
- **Email:** SMTP (Gmail)
- **Image Handling:** Pillow

## ✨ Key Features

- **Dual Selling Model:** Auction listings + Fixed-price listings
- **Real-time Auctions:** WebSocket-powered live bidding
- **Multi-seller Marketplace:** Cart checkout with multiple sellers
- **Stripe Integration:** Secure payments + seller payouts via Stripe Connect
- **Automated Tasks:** Celery for auction end processing, payment reminders
- **Messaging System:** Buyer-seller communication
- **Reviews & Ratings:** Product reviews + seller feedback
- **Province-based Filtering:** Filter products by region
- **Admin Dashboard:** Statistics and management tools
- **Wishlist & Cart:** Shopping cart for multiple items
- **Notifications:** Real-time + email notifications

---

## 📦 Full Project Setup

This project consists of **two repositories**:

1. **Backend (Django):** [github.com/abdul-542004/MadeInPK](https://github.com/abdul-542004/MadeInPK)
2. **Frontend (React + Vite):** [github.com/abdul-542004/MadeInPK-frontend](https://github.com/abdul-542004/MadeInPK-frontend)

### Clone Both Repositories

```bash
# Clone backend
git clone https://github.com/abdul-542004/MadeInPK.git
cd MadeInPK

# Clone frontend (in a separate directory)
git clone https://github.com/abdul-542004/MadeInPK-frontend.git
cd MadeInPK-frontend
```

---

## 🛠️ Installation Options

You have **3 options** to run the backend:

### **Option 1: Full Docker Setup** ✅ (Easiest)

Everything runs in Docker containers.

```bash
docker-compose build
docker-compose up
```

**Note:** If you encounter port conflicts, modify the ports in `docker-compose.yml`.

---

### **Option 2: Python Native + Docker for Services** ⭐ (Recommended)

Run Django/Celery natively, use Docker only for PostgreSQL and Redis.

**Why this option?** Minimal CPU/storage usage, easier debugging, faster hot-reloading.

#### **Linux Setup**

```bash
# 1. Clone the repository
git clone https://github.com/abdul-542004/MadeInPK.git
cd MadeInPK

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start PostgreSQL and Redis with Docker
docker run -d --name madeinpk_postgres \
  -e POSTGRES_DB=madeinpk_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=admin \
  -p 5432:5432 \
  postgres:15-alpine

docker run -d --name madeinpk_redis \
  -p 6379:6379 \
  redis:7-alpine

# 5. Create .env file (see Environment Variables section below)
cp .env.example .env
# Edit .env with your settings

# 6. Run migrations
python manage.py migrate

# 7. Populate initial data
python manage.py populate_categories
python manage.py populate_locations

# 8. Create superuser (optional)
python manage.py createsuperuser

# 9. Install Stripe CLI for webhooks
# Download from: https://stripe.com/docs/stripe-cli
# Or on Linux:
curl -s https://packages.stripe.com/api/v1/keys/pubkey-cli.asc | sudo apt-key add -
echo "deb https://packages.stripe.com/apt/ stable main" | sudo tee /etc/apt/sources.list.d/stripe.list
sudo apt update
sudo apt install stripe

# Login to Stripe
stripe login

# 10. Start all services using the script
chmod +x start.sh
./start.sh
```

#### **Windows Setup**

```bash
# 1. Clone the repository
git clone https://github.com/abdul-542004/MadeInPK.git
cd MadeInPK

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start PostgreSQL and Redis with Docker
docker run -d --name madeinpk_postgres ^
  -e POSTGRES_DB=madeinpk_db ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=admin ^
  -p 5432:5432 ^
  postgres:15-alpine

docker run -d --name madeinpk_redis ^
  -p 6379:6379 ^
  redis:7-alpine

# 5. Create .env file (see Environment Variables section below)
copy .env.example .env
# Edit .env with your settings

# 6. Run migrations
python manage.py migrate

# 7. Populate initial data
python manage.py populate_categories
python manage.py populate_locations

# 8. Create superuser (optional)
python manage.py createsuperuser

# 9. Install Stripe CLI for webhooks
# Download from: https://github.com/stripe/stripe-cli/releases/latest
# Extract and add to PATH

# Login to Stripe
stripe login

# 10. Start services manually (Windows doesn't support start.sh)
# Open 4 separate terminals and run:

# Terminal 1: Django Server
daphne -b 0.0.0.0 -p 8000 MadeInPK.asgi:application

# Terminal 2: Celery Worker
celery -A MadeInPK worker --loglevel=info

# Terminal 3: Celery Beat
celery -A MadeInPK beat --loglevel=info

# Terminal 4: Stripe Webhook Listener
stripe listen --forward-to localhost:8000/api/stripe/webhook/
```

---

### **Option 3: Python Native + Cloud Services** ☁️

Use third-party services (Neon for PostgreSQL, Upstash for Redis).

**Linux/Windows:**

```bash
# 1. Clone and setup virtual environment (same as Option 2, steps 1-3)

# 2. Sign up for services:
# - PostgreSQL: https://neon.tech (free tier)
# - Redis: https://upstash.com (free tier)

# 3. Configure .env with cloud credentials:
DB_HOST=your-neon-host.neon.tech
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
DB_PORT=5432

REDIS_URL=redis://default:your-password@your-redis.upstash.io:6379

# 4. Continue with migrations and starting services (same as Option 2, steps 6-10)
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```bash
# Django Settings
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:5173

# Database (for Option 2/3)
DB_NAME=madeinpk_db
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432

# Redis (for Option 2)
REDIS_URL=redis://localhost:6379/0

# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Getting Stripe Webhook Secret

```bash
# Start the Stripe listener
stripe listen --forward-to localhost:8000/api/stripe/webhook/

# Copy the webhook signing secret (whsec_...) to .env
```

---

## 📋 Management Commands

```bash
# Populate categories
python manage.py populate_categories

# Populate provinces and cities (Pakistan)
python manage.py populate_locations

# Create superuser
python manage.py createsuperuser
```

---

## 🌐 Running the Services

### Using start.sh (Linux/Mac)

```bash
chmod +x start.sh
./start.sh
```

This script automatically starts:
- Redis (if not running)
- Celery Worker (background)
- Celery Beat (background)
- Stripe Webhook Listener (background)
- Daphne ASGI Server (foreground)

### Manual Start (All Platforms)

Open 5 separate terminals:

```bash
# Terminal 1: ASGI Server (WebSockets + HTTP)
daphne -b 0.0.0.0 -p 8000 MadeInPK.asgi:application

# Terminal 2: Celery Worker
celery -A MadeInPK worker --loglevel=info

# Terminal 3: Celery Beat
celery -A MadeInPK beat --loglevel=info

# Terminal 4: Redis (if not using Docker)
redis-server

# Terminal 5: Stripe Webhook Listener
stripe listen --forward-to localhost:8000/api/stripe/webhook/
```

The backend will be running on: **http://localhost:8000**

---

## 🎨 Frontend Setup

```bash
cd MadeInPK-frontend
npm install
npm run dev
```

Frontend runs on: **http://localhost:5173**

---

## 📚 API Documentation

Full API documentation is available in the `docs/` folder:

- `docs/AUTHENTICATION_API.md` - User registration, login, profiles
- `docs/PRODUCTS_AND_LISTINGS_API.md` - Products, auctions, fixed-price listings
- `docs/CART_AND_PAYMENTS_API.md` - Shopping cart, checkout
- `docs/ORDERS_AND_PAYMENTS_API.md` - Orders, payments, Stripe
- `docs/MESSAGING_API.md` - Buyer-seller messaging
- `docs/SELLER_EARNINGS_API.md` - Seller dashboard, earnings
- `docs/WEBSOCKET_DOCUMENTATION.md` - Real-time auction WebSockets
- `docs/ADDITIONAL_FEATURES_API.md` - Reviews, wishlist, notifications

**Admin Panel:** http://localhost:8000/admin

---

## 🏗️ Project Structure

### Core Models (api/models.py)

- **User** - Extended user with buyer/seller roles
- **SellerProfile** - Seller business information
- **Province/City/Address** - Location hierarchy
- **Category** - Product categories
- **Product** - Base product model
- **AuctionListing** - Auction-based selling
- **FixedPriceListing** - Fixed-price selling with inventory
- **Bid** - Auction bids
- **Cart/CartItem** - Shopping cart
- **Order/OrderItem** - Purchase orders
- **Payment** - Stripe payments
- **SellerTransfer** - Seller payouts via Stripe Connect
- **Feedback** - Seller ratings (auction orders)
- **ProductReview** - Product reviews (fixed-price)
- **Conversation/Message** - Buyer-seller messaging
- **Notification** - User notifications
- **Wishlist** - Saved products

### Key Views (api/views.py)

**Authentication:**
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET/PUT /api/auth/profile/` - User profile
- `POST /api/auth/become-seller/` - Upgrade to seller

**Products & Listings:**
- `/api/products/` - CRUD for products
- `/api/auctions/` - Auction listings
- `/api/listings/` - Fixed-price listings
- `POST /api/auctions/{id}/place_bid/` - Place bid

**Shopping:**
- `/api/cart/` - Shopping cart
- `POST /api/cart/add_item/` - Add to cart
- `POST /api/cart/checkout/` - Checkout cart

**Orders:**
- `/api/orders/` - View orders
- `POST /api/orders/{id}/mark_shipped/` - Mark as shipped

**Seller:**
- `/api/seller/statistics/` - Dashboard stats
- `/api/seller/earnings/` - Earnings breakdown
- `/api/stripe/connect/` - Stripe Connect setup

**WebSocket Endpoint (api/consumers.py):**
- `ws://localhost:8000/ws/auction/{auction_id}/` - Real-time bidding

### URL Routing (api/urls.py)

All API endpoints are prefixed with `/api/` and follow RESTful conventions.

---

## 🔄 Background Tasks (Celery)

**Periodic Tasks (api/tasks.py):**
- `check_auction_endings` - Process ended auctions, create orders, notify winners
- `check_payment_deadlines` - Check expired payment deadlines, block non-paying users
- `send_pending_notifications` - Send queued email notifications

**Email Tasks:**
- `send_auction_won_email` - Email to auction winner with payment link
- `send_payment_success_email` - Email to buyer and seller after successful payment
- `send_account_blocked_email` - Notify user when account is blocked
- `send_feedback_request_email` - Request feedback after order delivery
- `send_outbid_notification_email` - Notify user when they're outbid

**Task Schedule (Celery Beat):**
- Auction ending checks: Every 5 minutes
- Payment deadline checks: Every 30 minutes
- Email notifications: Every 10 minutes

---

## 💳 Stripe Integration

### Setup Stripe Connect (Sellers)

1. Seller clicks "Setup Stripe" in dashboard
2. System creates Stripe Connect account
3. Seller completes onboarding
4. Seller can receive payments

### Payment Flow

**Single Seller (Auction/Direct Purchase):**
- Stripe creates Payment Intent with destination charge
- Platform fee (2%) deducted automatically
- Seller receives 98% directly to connected account

**Multi-Seller (Cart Checkout):**
- Stripe creates Checkout Session
- Platform collects full payment
- Celery creates separate transfers to each seller (98% of their items)



## 🐛 Common Issues

### Port Already in Use

**Linux/Mac:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill Redis
pkill redis-server

# Kill Celery
pkill -f celery
```

**Windows:**
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Connection Error

- Check if PostgreSQL container/service is running
- Verify `.env` database credentials
- Try: `docker restart madeinpk_postgres`

### Redis Connection Error

- Check if Redis is running
- Try: `docker restart madeinpk_redis`

### Stripe Webhook Not Working

- Ensure Stripe CLI is running: `stripe listen --forward-to localhost:8000/api/stripe/webhook/`
- Copy webhook secret to `.env`
- Check logs for errors



## 👥 Contributing

This is a educational project. Feel free to fork and modify.



## 🙋 Support

For issues or questions:
- Create an issue on GitHub
- Email: abdullahkhan542004@gmail.com

---

**Happy Coding! 🚀**
