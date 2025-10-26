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

## � Seller Profile Endpoints

### List Seller Profiles
```http
GET /api/seller-profiles/
```
**Auth Required:** Yes (Admins see all, sellers see own)

### Create Seller Profile
```http
POST /api/seller-profiles/
```
**Auth Required:** Yes (Sellers only)

**Body:**
```json
{
  "brand_name": "Artisan Crafts",
  "biography": "Handmade crafts from Pakistan...",
  "business_address": "123 Artisan Street, Lahore",
  "website": "https://artisan-crafts.pk",
  "social_media_links": {
    "facebook": "https://facebook.com/artisan",
    "instagram": "https://instagram.com/artisan"
  }
}
```

### Update Seller Profile
```http
PUT /api/seller-profiles/{id}/
```
**Auth Required:** Yes

### Verify Seller (Admin)
```http
POST /api/seller-profiles/{id}/verify/
```
**Auth Required:** Yes (Admin only)

### Unverify Seller (Admin)
```http
POST /api/seller-profiles/{id}/unverify/
```
**Auth Required:** Yes (Admin only)

---

## �📍 Location Endpoints

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

**Response includes for Fixed-Price Products:**
```json
{
  "id": 3,
  "name": "Handmade Carpet",
  "description": "Beautiful traditional carpet...",
  "price": "2500.00",
  "seller_username": "artisan_seller",
  "average_rating": 4.5,
  "total_reviews": 23,
  "seller_profile": {
    "brand_name": "Artisan Crafts",
    "biography": "Creating handmade products since 1990...",
    "is_verified": true,
    "average_rating": "4.75"
  },
  "images": [...],
  "listing_type": "fixed_price"
}
```

**Response for Auction Products (No reviews):**
```json
{
  "id": 5,
  "name": "Rare Antique Vase",
  "description": "Unique antique piece...",
  "seller_username": "antique_dealer",
  "average_rating": null,
  "total_reviews": 0,
  "seller_profile": null,
  "images": [...],
  "listing_type": "auction"
}
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

## ⭐ Product Review Endpoints (Fixed-Price Products Only)

### List Reviews
```http
GET /api/product-reviews/
GET /api/product-reviews/?product=1
GET /api/product-reviews/?rating=5
GET /api/product-reviews/?verified_only=true
```
**Auth Required:** No (Read-only is public)

**Query Parameters:**
- `product` - Filter by product ID
- `rating` - Filter by rating (1-5)
- `verified_only` - If `true`, only show verified purchases
- `ordering` - Sort by `created_at`, `rating`, `-created_at`, `-rating`

### Create Review
```http
POST /api/product-reviews/
```
**Auth Required:** Yes

**Body:**
```json
{
  "product": 3,
  "rating": 5,
  "title": "Excellent quality!",
  "comment": "This product exceeded my expectations. Highly recommended!",
  "order": 12
}
```

**Notes:**
- Only fixed-price products can be reviewed (auction products are rejected)
- One review per user per product
- If `order` is provided and matches buyer's order, review is marked as verified purchase
- Users can only review products, not auction items

### Update Review
```http
PUT /api/product-reviews/{id}/
```
**Auth Required:** Yes (Own reviews only)

**Body:**
```json
{
  "rating": 4,
  "title": "Updated review title",
  "comment": "Updated review content..."
}
```

### Delete Review
```http
DELETE /api/product-reviews/{id}/
```
**Auth Required:** Yes (Own reviews only)

### Review Detail
```http
GET /api/product-reviews/{id}/
```

**Response Example:**
```json
{
  "id": 1,
  "product": 3,
  "product_name": "Handmade Carpet",
  "buyer": 5,
  "buyer_username": "john_doe",
  "order": 12,
  "rating": 5,
  "title": "Excellent quality!",
  "comment": "This product exceeded my expectations...",
  "is_verified_purchase": true,
  "created_at": "2025-10-20T14:30:00Z",
  "updated_at": "2025-10-20T14:30:00Z"
}
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

- **Public**: Categories, Provinces, Cities, Product listings (read), Product reviews (read)
- **Authenticated**: Create products, place bids, purchase, messages, write reviews
- **Seller Only**: Create auctions/listings, mark shipped
- **Buyer Only**: Mark delivered, create feedback, write product reviews
- **Admin**: Access to admin panel at `/admin/`, verify sellers

---

## 📝 Important Notes

### Product Reviews vs Seller Feedback

**Product Reviews** (Fixed-Price Products Only):
- Pre-purchase reviews visible to all buyers
- Help buyers make informed decisions
- Include rating (1-5 stars), title, and comment
- Can be written by anyone who purchased the product
- Displayed on product detail page
- One review per user per product

**Seller Feedback** (All Orders - Auction & Fixed-Price):
- Post-purchase feedback given after delivery
- Evaluates seller performance and platform experience
- Only visible in aggregate (seller statistics)
- Includes seller rating, platform rating, communication, shipping speed
- One feedback per order
- Used to calculate seller's average rating

### Auction vs Fixed-Price Products

**Auction Products:**
- No product reviews
- Basic product information only
- Focus on bidding and auction details
- Unique items (quantity = 1)

**Fixed-Price Products:**
- Full review system enabled
- Average rating and review count displayed
- Seller profile information shown
- Can have bulk quantity
- Helps buyers make informed purchase decisions

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

// Get product with reviews (for fixed-price)
const getProductDetails = async (productId) => {
  const response = await fetch(`${API_URL}/products/${productId}/`);
  const product = await response.json();
  
  // If fixed-price product, fetch reviews
  if (product.listing_type === 'fixed_price') {
    const reviewsResponse = await fetch(`${API_URL}/product-reviews/?product=${productId}`);
    product.reviews = await reviewsResponse.json();
  }
  
  return product;
};

// Submit product review
const submitReview = async (productId, rating, title, comment, orderId = null) => {
  const response = await fetch(`${API_URL}/product-reviews/`, {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      product: productId,
      rating,
      title,
      comment,
      order: orderId
    })
  });
  return await response.json();
};
```
