# MadeInPK API Endpoints Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Most endpoints require authentication via Token. Include in headers:
```
Authorization: Token <your_token_here>
```

---

## 🔐 Authentication Endpoints

### Register User
```http
POST /api/auth/register/
```
**Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "03001234567",
  "role": "both"
}
```
**Response:** User object + token

### Login
```http
POST /api/auth/login/
```
**Body:**
```json
{
  "username": "john_doe",
  "password": "securepass123"
}
```
**Response:** User object + token

### Logout
```http
POST /api/auth/logout/
```
**Auth Required:** Yes

### Get Profile
```http
GET /api/auth/profile/
```
**Auth Required:** Yes

---

## 📍 Location Endpoints

### List Provinces
```http
GET /api/provinces/
```

### List Cities
```http
GET /api/cities/
GET /api/cities/?province=1
```

### Addresses (User)
```http
GET /api/addresses/
POST /api/addresses/
GET /api/addresses/{id}/
PUT /api/addresses/{id}/
DELETE /api/addresses/{id}/
POST /api/addresses/{id}/set_default/
```

**Create Address Body:**
```json
{
  "street_address": "123 Main Street",
  "city": 1,
  "postal_code": "54000",
  "is_default": true
}
```

---

## 📦 Product Endpoints

### List Products
```http
GET /api/products/
GET /api/products/?seller=1
GET /api/products/?category=2
GET /api/products/?condition=new
GET /api/products/?search=handmade
```

### Create Product
```http
POST /api/products/
```
**Auth Required:** Yes (Seller)

**Body:**
```json
{
  "category": 1,
  "name": "Handmade Carpet",
  "description": "Beautiful traditional carpet...",
  "condition": "new",
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ]
}
```

### Product Detail
```http
GET /api/products/{id}/
PUT /api/products/{id}/
DELETE /api/products/{id}/
```

### Add Product Image
```http
POST /api/products/{id}/add_image/
```
**Body:**
```json
{
  "image_url": "https://example.com/image.jpg",
  "is_primary": false,
  "order": 2
}
```

---

## 🔨 Auction Endpoints

### List Auctions
```http
GET /api/auctions/
GET /api/auctions/?status=active
GET /api/auctions/?seller=1
GET /api/auctions/?category=2
```

### Create Auction
```http
POST /api/auctions/
```
**Auth Required:** Yes (Seller)

**Body:**
```json
{
  "product_id": 5,
  "starting_price": "5000.00",
  "reserve_price": "8000.00",
  "start_time": "2025-10-26T10:00:00Z",
  "end_time": "2025-10-30T18:00:00Z"
}
```

### Auction Detail
```http
GET /api/auctions/{id}/
```

### Place Bid
```http
POST /api/auctions/{id}/place_bid/
```
**Auth Required:** Yes

**Body:**
```json
{
  "amount": "5500.00"
}
```

### List Bids
```http
GET /api/auctions/{id}/bids/
```

---

## 💰 Fixed Price Listing Endpoints

### List Listings
```http
GET /api/listings/
GET /api/listings/?status=active
GET /api/listings/?seller=1
GET /api/listings/?category=2
GET /api/listings/?min_price=1000
GET /api/listings/?max_price=10000
```

### Create Listing
```http
POST /api/listings/
```
**Auth Required:** Yes (Seller)

**Body:**
```json
{
  "product_id": 3,
  "price": "2500.00",
  "quantity": 10
}
```

### Listing Detail
```http
GET /api/listings/{id}/
PUT /api/listings/{id}/
DELETE /api/listings/{id}/
```

### Purchase Item
```http
POST /api/listings/{id}/purchase/
```
**Auth Required:** Yes

**Body:**
```json
{
  "quantity": 2,
  "shipping_address": 1
}
```

---

## 📋 Order Endpoints

### List Orders
```http
GET /api/orders/
GET /api/orders/?status=paid
GET /api/orders/?role=buyer
GET /api/orders/?role=seller
```
**Auth Required:** Yes

### Order Detail
```http
GET /api/orders/{id}/
```

### Mark as Shipped (Seller)
```http
POST /api/orders/{id}/mark_shipped/
```
**Auth Required:** Yes (Seller only)

### Mark as Delivered (Buyer)
```http
POST /api/orders/{id}/mark_delivered/
```
**Auth Required:** Yes (Buyer only)

---

## ⭐ Feedback Endpoints

### List Feedback
```http
GET /api/feedbacks/
GET /api/feedbacks/?seller=2
```

### Create Feedback
```http
POST /api/feedbacks/
```
**Auth Required:** Yes (Buyer)

**Body:**
```json
{
  "order_id": 5,
  "seller_rating": 5,
  "seller_comment": "Great seller, fast shipping!",
  "platform_rating": 4,
  "platform_comment": "Good experience overall",
  "communication_rating": 5,
  "product_as_described": true,
  "shipping_speed_rating": 5
}
```

### Seller Statistics
```http
GET /api/feedbacks/seller_stats/?seller_id=2
```

---

## 💬 Messaging Endpoints

### List Conversations
```http
GET /api/conversations/
```
**Auth Required:** Yes

### Conversation Messages
```http
GET /api/conversations/{id}/messages/
```

### Send Message
```http
POST /api/conversations/{id}/send_message/
```
**Body:**
```json
{
  "content": "Hello, when will you ship my order?"
}
```

---

## 🔔 Notification Endpoints

### List Notifications
```http
GET /api/notifications/
```
**Auth Required:** Yes

### Mark as Read
```http
POST /api/notifications/{id}/mark_read/
```

### Mark All as Read
```http
POST /api/notifications/mark_all_read/
```

---

## 📝 Complaint Endpoints

### List Complaints
```http
GET /api/complaints/
```
**Auth Required:** Yes

### Create Complaint
```http
POST /api/complaints/
```
**Body:**
```json
{
  "category": "seller",
  "subject": "Seller not responding",
  "description": "The seller has not shipped my order after 5 days...",
  "order": 3,
  "seller": 2
}
```

### Complaint Detail
```http
GET /api/complaints/{id}/
```

---

## 🔌 WebSocket Endpoints

### Auction Real-time Bidding
```javascript
// Connect to auction WebSocket
const socket = new WebSocket('ws://localhost:8000/ws/auction/1/');

// Listen for messages
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Message:', data);
    
    if (data.type === 'new_bid') {
        // Update UI with new bid
        console.log('New bid:', data.data);
    }
    
    if (data.type === 'auction_ended') {
        // Auction ended
        console.log('Auction ended:', data.data);
    }
};

// Place a bid
socket.send(JSON.stringify({
    type: 'place_bid',
    amount: '5500.00'
}));
```

---

## 📊 Common Query Parameters

### Pagination
```
?page=2
```

### Search
```
?search=carpet
```

### Ordering
```
?ordering=-created_at
?ordering=price
```

### Filters
Most list endpoints support filtering by:
- `status` - Filter by status
- `seller` - Filter by seller ID
- `category` - Filter by category ID
- `created_at__gte` - Created after date
- `created_at__lte` - Created before date

---

## 🔒 Permissions

- **Public**: Categories, Provinces, Cities, Product listings (read)
- **Authenticated**: Create products, place bids, purchase, messages
- **Seller Only**: Create auctions/listings, mark shipped
- **Buyer Only**: Mark delivered, create feedback
- **Admin**: Access to admin panel at `/admin/`

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "error": "Bid must be higher than current price"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "Your account is blocked"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## 🧪 Testing with cURL

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "role": "buyer"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### List Auctions (with token)
```bash
curl -X GET http://localhost:8000/api/auctions/ \
  -H "Authorization: Token your_token_here"
```

---

## 📱 React Frontend Integration Example

```javascript
// API Client
const API_URL = 'http://localhost:8000/api';
const token = localStorage.getItem('token');

// Fetch auctions
const fetchAuctions = async () => {
  const response = await fetch(`${API_URL}/auctions/`, {
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return await response.json();
};

// Place bid
const placeBid = async (auctionId, amount) => {
  const response = await fetch(`${API_URL}/auctions/${auctionId}/place_bid/`, {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ amount })
  });
  return await response.json();
};
```
