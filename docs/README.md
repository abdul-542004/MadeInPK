# MadeInPK API Documentation

Complete API documentation for the MadeInPK e-commerce platform - a C2C marketplace for Pakistani artisans, manufacturers, and small businesses.

---

## 📚 Documentation Structure

This documentation is split into multiple focused files for easy navigation:

### 1. [WebSocket Documentation](./WEBSOCKET_DOCUMENTATION.md)
Real-time bidding functionality using Django Channels.

**Topics Covered:**
- Auction WebSocket connection
- Real-time bid updates
- Message types and formats
- React hooks and examples
- Connection management
- Error handling

**Key Features:**
- Live auction updates
- Real-time bid notifications
- Automatic reconnection
- Multi-client synchronization

---

### 2. [Authentication API](./AUTHENTICATION_API.md)
User registration, login, and profile management.

**Endpoints:**
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile

**Topics Covered:**
- Token-based authentication
- User roles (buyer, seller, both, admin)
- Profile management
- React authentication context
- Security best practices

---

### 3. [Products & Listings API](./PRODUCTS_AND_LISTINGS_API.md)
Product management, auctions, and fixed-price listings.

**Endpoints:**
- `/api/categories/` - Product categories
- `/api/products/` - Product CRUD operations
- `/api/auctions/` - Auction listings
- `/api/listings/` - Fixed-price listings

**Topics Covered:**
- Product creation with images
- Auction management
- Fixed-price listings
- Bidding (REST API)
- Search and filtering
- Sample data reference

---

### 4. [Orders & Payments API](./ORDERS_AND_PAYMENTS_API.md)
Order management and payment processing.

**Endpoints:**
- `/api/orders/` - Order management
- `/api/orders/{id}/mark_shipped/` - Mark as shipped
- `/api/orders/{id}/mark_delivered/` - Mark as delivered

**Topics Covered:**
- Order creation and tracking
- Payment flow with Stripe
- Order status management
- Platform fees (2%)
- Payment deadlines
- Complete purchase flow examples

---

### 5. [Additional Features API](./ADDITIONAL_FEATURES_API.md)
Supporting features like wishlist, messaging, notifications, etc.

**Endpoints:**
- `/api/provinces/` & `/api/cities/` - Location data
- `/api/addresses/` - Address management
- `/api/wishlist/` - Wishlist functionality
- `/api/feedbacks/` - Order feedback
- `/api/product-reviews/` - Product reviews
- `/api/conversations/` - Messaging
- `/api/notifications/` - Notifications
- `/api/seller-profiles/` - Seller profiles
- `/api/complaints/` - Complaint system

---

## 🚀 Quick Start

### Base URLs

```
REST API:    http://localhost:8000/api/
WebSocket:   ws://localhost:8000/ws/
```

### Authentication

All authenticated requests require a token in the header:

```
Authorization: Token <your_token_here>
```

### Example: Login and Make Request

```javascript
// 1. Login
const loginResponse = await axios.post(
  'http://localhost:8000/api/auth/login/',
  {
    email: 'buyer1@example.com',
    password: 'password123'
  }
);

const token = loginResponse.data.token;

// 2. Make authenticated request
const productsResponse = await axios.get(
  'http://localhost:8000/api/products/',
  {
    headers: {
      'Authorization': `Token ${token}`
    }
  }
);
```

---

## 🧪 Test Accounts

Use these accounts for testing (password: `password123` for all):

| Username | Email | Role | Description |
|----------|-------|------|-------------|
| buyer1 | buyer1@example.com | buyer | Regular buyer |
| buyer2 | buyer2@example.com | buyer | Regular buyer |
| buyer3 | buyer3@example.com | buyer | Regular buyer |
| seller1 | seller1@example.com | seller | Verified seller (Hassan Textiles) |
| seller2 | seller2@example.com | seller | Verified seller (Ayesha Crafts) |
| seller3 | seller3@example.com | seller | Unverified seller (Ahmed Pottery) |
| seller4 | seller4@example.com | both | Buyer & Seller (Zara Jewelry) |
| buyer_seller1 | buyer_seller1@example.com | both | Buyer & Seller |

---

## 📦 Sample Data

The database is populated with sample data including:

### Categories (8)
- Textiles
- Handicrafts
- Pottery
- Jewelry
- Home Decor
- Carpets
- Leather Goods
- Woodwork

### Products (11)
- 6 Auction listings
- 5 Fixed-price listings
- Multiple images per product
- Various price ranges

### Locations
- 7 Provinces
- 30+ Cities across Pakistan

---

## 🔑 Key Features

### For Buyers
- Browse products by category
- Search and filter
- Place bids on auctions (real-time)
- Purchase fixed-price items
- Track orders
- Leave feedback and reviews
- Wishlist functionality
- Message sellers
- Receive notifications

### For Sellers
- Create products with images
- List items as auction or fixed-price
- Manage inventory
- Process orders
- Track sales
- Receive payments (minus 2% fee)
- Build seller profile
- Communicate with buyers

### Platform Features
- Real-time auction bidding (WebSocket)
- Secure payments via Stripe
- 2% platform commission
- User blocking for non-payment
- Complaint system
- Email notifications
- Seller verification
- Product reviews

---

## 🏗️ Tech Stack

**Backend:**
- Django 5.2.7
- Django REST Framework
- Django Channels (WebSocket)
- PostgreSQL
- Redis (for Channels)
- Celery (background tasks)
- Stripe (payments)

**Frontend (Recommended):**
- React
- Axios for API calls
- WebSocket for real-time features

---

## 📊 API Response Format

### Success Response

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response

```json
{
  "error": "Error message here"
}
```

Or field-specific errors:

```json
{
  "field_name": ["Error message for this field"],
  "another_field": ["Another error message"]
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource not found |
| 500 | Server Error - Internal error |

---

## 🔍 Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

**Example:**
```
GET /api/products/?page=2&page_size=20
```

---

## 🔎 Search & Filtering

### Search
Most list endpoints support search:

```
GET /api/products/?search=shawl
GET /api/auctions/?search=pottery
```

### Filtering
Filter by specific fields:

```
GET /api/products/?category=1&condition=new
GET /api/auctions/?status=active&seller=5
GET /api/listings/?min_price=1000&max_price=5000
```

### Ordering
Sort results:

```
GET /api/products/?ordering=-created_at
GET /api/auctions/?ordering=end_time
GET /api/listings/?ordering=price
```

**Ordering Options:**
- `field_name` - Ascending order
- `-field_name` - Descending order

---

## 🌐 CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)

For production, update `CORS_ALLOWED_ORIGINS` in `settings.py`.

---

## 🔐 Security Notes

### Token Storage
- Store tokens in `localStorage` for development
- Use httpOnly cookies for production
- Never expose tokens in URLs

### HTTPS
- Always use HTTPS in production
- Update API URLs to use `https://`

### Input Validation
- All inputs are validated on the backend
- Frontend should also validate for better UX

---

## 📱 WebSocket Connection

For real-time auction updates:

```javascript
const socket = new WebSocket(
  `ws://localhost:8000/ws/auction/1/?token=${token}`
);

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle auction updates
};
```

See [WebSocket Documentation](./WEBSOCKET_DOCUMENTATION.md) for complete details.

---

## 🛠️ Development Tips

### Axios Configuration

```javascript
import axios from 'axios';

// Set base URL
axios.defaults.baseURL = 'http://localhost:8000/api/';

// Set auth token from localStorage
const token = localStorage.getItem('authToken');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Token ${token}`;
}

// Handle 401 errors globally
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Environment Variables

```javascript
// .env file
REACT_APP_API_URL=http://localhost:8000/api/
REACT_APP_WS_URL=ws://localhost:8000/ws/

// Usage
const API_URL = process.env.REACT_APP_API_URL;
```

---

## 📞 Support

For questions or issues:
1. Check the relevant documentation file
2. Review error messages carefully
3. Verify authentication token is valid
4. Check request body format matches examples

---

## 📄 License

This API documentation is part of the MadeInPK project.

---

## 🔄 Version History

**Version 1.0** (October 2025)
- Initial API documentation
- WebSocket support for auctions
- Complete REST API coverage
- Sample data and test accounts

---

**Happy Coding! 🚀**
