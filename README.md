# MadeInPK - E-Commerce Platform Backend

MadeInPK is a C2C e-commerce platform that empowers Pakistani artisans, manufacturers, and small businesses by combining fixed-price selling with real-time auctions.

## Tech Stack

- **Backend**: Django 5.2.7 + Django REST Framework
- **Database**: PostgreSQL
- **Real-time**: WebSockets (Django Channels)
- **Task Queue**: Celery with Redis
- **Payment**: Stripe Connect
- **Email**: SMTP (Celery for async emails)

## Features

- Dual listing system (Auction + Fixed Price)
- Real-time bidding via WebSockets
- Stripe Connect for payment processing with 2% platform fee
- Buyer-seller messaging system
- Feedback system for sellers and platform
- Automated notification system
- Non-paying user tracking and blocking
- Complaint management system

## Setup Instructions

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE madeinpk_db;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE madeinpk_db TO postgres;
\q
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your actual credentials
nano .env
```

### 5. Django Setup

```bash
cd MadeInPK

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### 6. Start Services

**Terminal 1 - Django ASGI Server (Daphne - for WebSockets):**
```bash
# Use Daphne instead of runserver to handle WebSockets
daphne -b 0.0.0.0 -p 8000 MadeInPK.asgi:application

# OR for development with auto-reload:
daphne -b 0.0.0.0 -p 8000 MadeInPK.asgi:application --reload
```

**Terminal 2 - Celery Worker:**
```bash
celery -A MadeInPK worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
celery -A MadeInPK beat --loglevel=info
```

**Terminal 4 - Redis (if not running as service):**
```bash
redis-server
```

## Important Notes

### WebSocket Support
⚠️ **DO NOT use `python manage.py runserver`** - it does not support WebSockets!

Use **Daphne** (ASGI server) instead:
```bash
daphne MadeInPK.asgi:application
```

For production, use Daphne with proper workers:
```bash
daphne -u /tmp/daphne.sock MadeInPK.asgi:application
```

## API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout

### Products
- `GET /api/products/` - List all products
- `POST /api/products/` - Create product (seller only)
- `GET /api/products/{id}/` - Product detail
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product

### Auctions
- `GET /api/auctions/` - List active auctions
- `POST /api/auctions/` - Create auction (seller only)
- `GET /api/auctions/{id}/` - Auction detail
- `POST /api/auctions/{id}/bids/` - Place bid

### Fixed Price Listings
- `GET /api/listings/` - List all fixed price listings
- `POST /api/listings/` - Create listing (seller only)
- `POST /api/listings/{id}/purchase/` - Purchase item

### Orders
- `GET /api/orders/` - User's orders
- `GET /api/orders/{id}/` - Order detail
- `POST /api/orders/{id}/mark-shipped/` - Mark as shipped (seller)

### Messages
- `GET /api/conversations/` - List conversations
- `GET /api/conversations/{id}/messages/` - Get messages
- `POST /api/conversations/{id}/messages/` - Send message

### Feedback
- `POST /api/orders/{id}/feedback/` - Submit feedback
- `GET /api/sellers/{id}/feedback/` - View seller feedback

### Complaints
- `POST /api/complaints/` - Submit complaint
- `GET /api/complaints/` - List user's complaints

## WebSocket Endpoints

### Auction Bidding
```javascript
ws://localhost:8000/ws/auction/{auction_id}/

// Messages
{
  "type": "place_bid",
  "amount": "5000.00"
}
```

## Data Models

### Core Models:
- **User** - Extended user with role (buyer/seller/both)
- **Product** - Base product information
- **AuctionListing** - Auction-specific details
- **FixedPriceListing** - Fixed price listings
- **Bid** - Auction bids
- **Order** - Purchase orders
- **Payment** - Stripe payment records

### Supporting Models:
- **Province, City, Address** - Normalized location data
- **Category** - Product categorization
- **Conversation, Message** - Messaging system
- **Feedback** - Ratings and reviews
- **Notification** - System notifications
- **Complaint** - User complaints
- **PaymentViolation** - Track non-paying users

## Celery Tasks

- `check_auction_endings` - Process ended auctions (every 5 min)
- `check_payment_deadlines` - Check expired payments (every 30 min)
- `send_pending_notifications` - Send email notifications (every 10 min)
- `send_auction_won_email` - Email to auction winner
- `send_payment_success_email` - Email after payment
- `send_feedback_request_email` - Request feedback after delivery

## Stripe Integration

1. Create Stripe account and get API keys
2. Set up Stripe Connect for sellers
3. Configure webhook endpoint: `/api/stripe/webhook/`
4. Platform fee: 2% of transaction

## Development Notes

- Custom User model: `api.User`
- Timezone: Asia/Karachi
- Database normalized to BCNF
- WebSockets for real-time bidding
- REST APIs for everything else
- Products can be EITHER auction OR fixed-price (not both)

## Testing

```bash
python manage.py test api
```

## Production Deployment

1. Set `DEBUG=False`
2. Update `ALLOWED_HOSTS`
3. Use environment variables for secrets
4. Set up proper PostgreSQL with connection pooling
5. Use production ASGI server (Daphne/Uvicorn)
6. Set up Nginx reverse proxy
7. Use Redis Sentinel for high availability
8. Configure proper email backend
9. Set up Stripe production keys

## License

Proprietary - MadeInPK Platform
