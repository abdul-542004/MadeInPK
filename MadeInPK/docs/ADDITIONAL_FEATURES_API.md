# MadeInPK Additional Features API

**Base URL:** `http://localhost:8000/api/`

---

## Table of Contents

1. [Location APIs](#location-apis)
2. [Wishlist](#wishlist)
3. [Feedback & Reviews](#feedback--reviews)
4. [Messaging](#messaging)
5. [Notifications](#notifications)
6. [Seller Profiles](#seller-profiles)
7. [Complaints](#complaints)

---

## Location APIs

### List Provinces

**Endpoint:** `GET /api/provinces/`

**Authentication:** Not required

**Response (200 OK):**

```json
{
  "count": 7,
  "next": null,
  "previous": null,
  "results": [
    {"id": 1, "name": "Punjab"},
    {"id": 2, "name": "Sindh"},
    {"id": 3, "name": "Khyber Pakhtunkhwa"},
    {"id": 4, "name": "Balochistan"},
    {"id": 5, "name": "Islamabad Capital Territory"},
    {"id": 6, "name": "Gilgit-Baltistan"},
    {"id": 7, "name": "Azad Jammu and Kashmir"}
  ]
}
```

### List Cities

**Endpoint:** `GET /api/cities/`

**Authentication:** Not required

**Query Parameters:**
- `province` - Filter by province ID

**Example:** `GET /api/cities/?province=1`

**Response (200 OK):**

```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {"id": 1, "name": "Lahore", "province": 1, "province_name": "Punjab"},
    {"id": 2, "name": "Faisalabad", "province": 1, "province_name": "Punjab"},
    {"id": 3, "name": "Rawalpindi", "province": 1, "province_name": "Punjab"},
    {"id": 4, "name": "Multan", "province": 1, "province_name": "Punjab"},
    {"id": 5, "name": "Gujranwala", "province": 1, "province_name": "Punjab"},
    {"id": 6, "name": "Sialkot", "province": 1, "province_name": "Punjab"}
  ]
}
```

### List User Addresses

**Endpoint:** `GET /api/addresses/`

**Authentication:** Required

**Response (200 OK):**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "street_address": "456 Main Street",
      "city": 1,
      "city_name": "Lahore",
      "province_name": "Punjab",
      "postal_code": "54000",
      "is_default": true,
      "created_at": "2025-10-20T10:00:00Z"
    },
    {
      "id": 2,
      "street_address": "789 Commercial Area",
      "city": 7,
      "city_name": "Karachi",
      "province_name": "Sindh",
      "postal_code": "75500",
      "is_default": false,
      "created_at": "2025-10-22T14:30:00Z"
    }
  ]
}
```

### Create Address

**Endpoint:** `POST /api/addresses/`

**Authentication:** Required

**Request Body:**

```json
{
  "street_address": "123 New Street",
  "city": 7,
  "postal_code": "75500",
  "is_default": false
}
```

**Response (201 Created):**

```json
{
  "id": 3,
  "street_address": "123 New Street",
  "city": 7,
  "city_name": "Karachi",
  "province_name": "Sindh",
  "postal_code": "75500",
  "is_default": false,
  "created_at": "2025-10-27T19:30:00Z"
}
```

### Update Address

**Endpoint:** `PUT /api/addresses/{id}/` or `PATCH /api/addresses/{id}/`

**Authentication:** Required

### Delete Address

**Endpoint:** `DELETE /api/addresses/{id}/`

**Authentication:** Required

### Set Default Address

**Endpoint:** `POST /api/addresses/{id}/set_default/`

**Authentication:** Required

**Response (200 OK):**

```json
{
  "message": "Default address updated"
}
```

---

## Wishlist

### List Wishlist Items

**Endpoint:** `GET /api/wishlist/`

**Authentication:** Required

**Query Parameters:**
- `ordering` - Sort field (`created_at`, `-created_at`)

**Response (200 OK):**

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product": 1,
      "product_name": "Handwoven Pashmina Shawl",
      "product_image": "http://localhost:8000/media/products/pashmina_shawl.jpg",
      "seller": "seller1",
      "seller_id": 5,
      "category": "Textiles",
      "category_id": 1,
      "price": {
        "current_price": "2875.00",
        "starting_price": "2500.00"
      },
      "stock_status": "In Stock",
      "listing_type": "auction",
      "notes": "Want to bid on this before it ends",
      "created_at": "2025-10-27T10:00:00Z"
    },
    {
      "id": 2,
      "product": 2,
      "product_name": "Embroidered Cotton Kurti",
      "product_image": "http://localhost:8000/media/products/embroidered_kurti.jpg",
      "seller": "seller1",
      "seller_id": 5,
      "category": "Textiles",
      "category_id": 1,
      "price": {
        "price": "1200.00"
      },
      "stock_status": "In Stock",
      "listing_type": "fixed_price",
      "notes": "Buy for sister's birthday",
      "created_at": "2025-10-26T15:30:00Z"
    },
    {
      "id": 3,
      "product": 8,
      "product_name": "Silver Enamel Necklace",
      "product_image": "http://localhost:8000/media/products/silver_necklace.jpg",
      "seller": "seller4",
      "seller_id": 8,
      "category": "Jewelry",
      "category_id": 4,
      "price": {
        "price": "2850.00"
      },
      "stock_status": "In Stock",
      "listing_type": "fixed_price",
      "notes": "",
      "created_at": "2025-10-25T12:00:00Z"
    }
  ]
}
```

### Add to Wishlist

**Endpoint:** `POST /api/wishlist/`

**Authentication:** Required

**Request Body:**

```json
{
  "product": 1,
  "notes": "Want to bid on this before it ends"
}
```

**Response (201 Created):**

```json
{
  "id": 4,
  "product": 1,
  "product_name": "Handwoven Pashmina Shawl",
  "product_image": "http://localhost:8000/media/products/pashmina_shawl.jpg",
  "seller": "seller1",
  "seller_id": 5,
  "category": "Textiles",
  "category_id": 1,
  "price": {
    "current_price": "2875.00",
    "starting_price": "2500.00"
  },
  "stock_status": "In Stock",
  "listing_type": "auction",
  "notes": "Want to bid on this before it ends",
  "created_at": "2025-10-27T19:30:00Z"
}
```

**Error (400 Bad Request):**

```json
{
  "product": ["Product is already in your wishlist"]
}
```

### Remove from Wishlist

**Endpoint:** `DELETE /api/wishlist/{id}/`

**Authentication:** Required

**Response (204 No Content)**

---

## Feedback & Reviews

### Submit Feedback (for Orders)

**Endpoint:** `POST /api/feedbacks/`

**Authentication:** Required (Buyer only, after delivery)

**Request Body:**

```json
{
  "order_id": 1,
  "seller_rating": 5,
  "seller_comment": "Excellent seller! Fast shipping and great communication.",
  "platform_rating": 5,
  "platform_comment": "Great platform, easy to use",
  "communication_rating": 5,
  "product_as_described": true,
  "shipping_speed_rating": 5
}
```

**Request Fields:**

| Field | Type | Required | Range | Description |
|-------|------|----------|-------|-------------|
| order_id | integer | Yes | - | Order ID to review |
| seller_rating | integer | Yes | 1-5 | Overall seller rating |
| seller_comment | text | No | - | Comment about seller |
| platform_rating | integer | Yes | 1-5 | Platform rating |
| platform_comment | text | No | - | Comment about platform |
| communication_rating | integer | Yes | 1-5 | Seller communication rating |
| product_as_described | boolean | Yes | - | Was product as described? |
| shipping_speed_rating | integer | Yes | 1-5 | Shipping speed rating |

**Response (201 Created):**

```json
{
  "id": 1,
  "order": 1,
  "order_number": "FXD-A1B2C3D4E5F6",
  "buyer": 1,
  "buyer_username": "buyer1",
  "seller_rating": 5,
  "seller_comment": "Excellent seller! Fast shipping and great communication.",
  "platform_rating": 5,
  "platform_comment": "Great platform, easy to use",
  "communication_rating": 5,
  "product_as_described": true,
  "shipping_speed_rating": 5,
  "created_at": "2025-10-27T19:30:00Z"
}
```

**Error Responses:**

```json
{
  "error": "Order not found or you are not the buyer"
}
```

```json
{
  "error": "Order must be delivered before feedback"
}
```

```json
{
  "error": "Feedback already submitted"
}
```

### Get Seller Feedback

**Endpoint:** `GET /api/feedbacks/?seller={seller_id}`

**Authentication:** Not required

**Response (200 OK):**

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "order_number": "FXD-A1B2C3D4E5F6",
      "buyer_username": "buyer1",
      "seller_rating": 5,
      "seller_comment": "Excellent seller!",
      "communication_rating": 5,
      "product_as_described": true,
      "shipping_speed_rating": 5,
      "created_at": "2025-10-27T19:30:00Z"
    }
  ]
}
```

### Get Seller Statistics

**Endpoint:** `GET /api/feedbacks/seller_stats/?seller_id={seller_id}`

**Authentication:** Not required

**Response (200 OK):**

```json
{
  "total_feedbacks": 12,
  "average_seller_rating": 4.7,
  "average_communication": 4.8,
  "average_shipping": 4.6,
  "product_as_described_percent": 95.5
}
```

### Product Reviews (Fixed Price Only)

#### List Product Reviews

**Endpoint:** `GET /api/product-reviews/?product={product_id}`

**Authentication:** Not required

**Query Parameters:**
- `product` - Filter by product ID
- `rating` - Filter by rating (1-5)
- `verified_only` - Show only verified purchases (`true`/`false`)

**Response (200 OK):**

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "product": 2,
      "product_name": "Embroidered Cotton Kurti",
      "buyer": 1,
      "buyer_username": "buyer1",
      "order": 1,
      "rating": 5,
      "title": "Beautiful kurti!",
      "comment": "Love the embroidery work. Fits perfectly and the quality is excellent.",
      "is_verified_purchase": true,
      "created_at": "2025-10-27T19:00:00Z",
      "updated_at": "2025-10-27T19:00:00Z"
    },
    {
      "id": 2,
      "product": 2,
      "product_name": "Embroidered Cotton Kurti",
      "buyer": 3,
      "buyer_username": "buyer3",
      "order": null,
      "rating": 4,
      "title": "Good quality",
      "comment": "Nice product, would recommend",
      "is_verified_purchase": false,
      "created_at": "2025-10-26T15:00:00Z",
      "updated_at": "2025-10-26T15:00:00Z"
    }
  ]
}
```

#### Submit Product Review

**Endpoint:** `POST /api/product-reviews/`

**Authentication:** Required

**Request Body:**

```json
{
  "product": 2,
  "rating": 5,
  "title": "Beautiful kurti!",
  "comment": "Love the embroidery work. Fits perfectly and the quality is excellent.",
  "order": 1
}
```

**Note:** If `order` is provided and valid, review is marked as verified purchase.

**Response (201 Created):**

```json
{
  "id": 3,
  "product": 2,
  "product_name": "Embroidered Cotton Kurti",
  "buyer": 1,
  "buyer_username": "buyer1",
  "order": 1,
  "rating": 5,
  "title": "Beautiful kurti!",
  "comment": "Love the embroidery work. Fits perfectly and the quality is excellent.",
  "is_verified_purchase": true,
  "created_at": "2025-10-27T19:30:00Z",
  "updated_at": "2025-10-27T19:30:00Z"
}
```

**Error Responses:**

```json
{
  "product": ["Auction products cannot be reviewed"]
}
```

```json
{
  "non_field_errors": ["You have already reviewed this product"]
}
```

---

## Messaging

### List Conversations

**Endpoint:** `GET /api/conversations/`

**Authentication:** Required

**Response (200 OK):**

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "buyer": 1,
      "buyer_username": "buyer1",
      "seller": 5,
      "seller_username": "seller1",
      "order": 1,
      "order_number": "FXD-A1B2C3D4E5F6",
      "latest_message": {
        "id": 5,
        "sender": 5,
        "sender_username": "seller1",
        "content": "I will ship it tomorrow morning",
        "is_read": false,
        "created_at": "2025-10-27T18:30:00Z"
      },
      "unread_count": 1,
      "created_at": "2025-10-27T18:00:00Z",
      "updated_at": "2025-10-27T18:30:00Z"
    }
  ]
}
```

### Get Conversation Messages

**Endpoint:** `GET /api/conversations/{id}/messages/`

**Authentication:** Required (Participant only)

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "sender": 1,
    "sender_username": "buyer1",
    "content": "When will you ship the item?",
    "is_read": true,
    "created_at": "2025-10-27T18:00:00Z"
  },
  {
    "id": 2,
    "sender": 5,
    "sender_username": "seller1",
    "content": "I will ship it tomorrow morning",
    "is_read": true,
    "created_at": "2025-10-27T18:30:00Z"
  }
]
```

**Note:** Messages are automatically marked as read when retrieved.

### Send Message

**Endpoint:** `POST /api/conversations/{id}/send_message/`

**Authentication:** Required (Participant only)

**Request Body:**

```json
{
  "content": "Thank you! Looking forward to receiving it."
}
```

**Response (201 Created):**

```json
{
  "id": 3,
  "sender": 1,
  "sender_username": "buyer1",
  "content": "Thank you! Looking forward to receiving it.",
  "is_read": false,
  "created_at": "2025-10-27T18:45:00Z"
}
```

**Error (403 Forbidden):**

```json
{
  "error": "You are not part of this conversation"
}
```

---

## Notifications

### List Notifications

**Endpoint:** `GET /api/notifications/`

**Authentication:** Required

**Response (200 OK):**

```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "notification_type": "bid_outbid",
      "title": "You have been outbid",
      "message": "Someone placed a higher bid on Handwoven Pashmina Shawl",
      "is_read": false,
      "order": null,
      "auction": 1,
      "created_at": "2025-10-27T18:32:00Z"
    },
    {
      "id": 2,
      "notification_type": "order_shipped",
      "title": "Your order has been shipped",
      "message": "Your order FXD-A1B2C3D4E5F6 has been shipped",
      "is_read": false,
      "order": 1,
      "auction": null,
      "created_at": "2025-10-27T17:00:00Z"
    },
    {
      "id": 3,
      "notification_type": "payment_reminder",
      "title": "Complete your payment",
      "message": "Please complete payment for Embroidered Cotton Kurti",
      "is_read": true,
      "order": 1,
      "auction": null,
      "created_at": "2025-10-27T16:00:00Z"
    }
  ]
}
```

### Notification Types

| Type | Description |
|------|-------------|
| `bid_placed` | New bid placed on your auction |
| `bid_outbid` | You've been outbid |
| `auction_won` | You won an auction |
| `auction_lost` | You lost an auction |
| `auction_ended` | Auction ended |
| `payment_reminder` | Payment reminder |
| `payment_received` | Payment received (seller) |
| `order_shipped` | Order shipped |
| `order_delivered` | Order delivered |
| `feedback_request` | Request for feedback |
| `message_received` | New message received |
| `account_blocked` | Account blocked |
| `general` | General notification |

### Mark Notification as Read

**Endpoint:** `POST /api/notifications/{id}/mark_read/`

**Authentication:** Required

**Response (200 OK):**

```json
{
  "message": "Notification marked as read"
}
```

### Mark All Notifications as Read

**Endpoint:** `POST /api/notifications/mark_all_read/`

**Authentication:** Required

**Response (200 OK):**

```json
{
  "message": "All notifications marked as read"
}
```

---

## Seller Profiles

### Get Seller Profile

**Endpoint:** `GET /api/seller-profiles/{id}/`

**Authentication:** Not required

**Response (200 OK):**

```json
{
  "id": 1,
  "user": 5,
  "user_username": "seller1",
  "user_email": "seller1@example.com",
  "brand_name": "Hassan Textiles",
  "biography": "Family-owned textile business for 3 generations, specializing in handwoven fabrics.",
  "business_address": "123 Textile Market, Faisalabad, Punjab",
  "website": "https://hassantextiles.pk",
  "social_media_links": {
    "facebook": "https://facebook.com/hassantextiles",
    "instagram": "https://instagram.com/hassantextiles"
  },
  "is_verified": true,
  "average_rating": "4.70",
  "total_feedbacks": 12,
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-27T15:30:00Z"
}
```

### Create Seller Profile

**Endpoint:** `POST /api/seller-profiles/`

**Authentication:** Required (Seller role)

**Request Body:**

```json
{
  "brand_name": "My Artisan Brand",
  "biography": "Artisan specializing in traditional Pakistani crafts",
  "business_address": "123 Craft Street, Lahore, Punjab",
  "website": "https://myartisanbrand.com",
  "social_media_links": {
    "facebook": "https://facebook.com/myartisanbrand",
    "instagram": "https://instagram.com/myartisanbrand"
  }
}
```

**Response (201 Created):**

```json
{
  "id": 5,
  "user": 9,
  "user_username": "newuser",
  "user_email": "newuser@example.com",
  "brand_name": "My Artisan Brand",
  "biography": "Artisan specializing in traditional Pakistani crafts",
  "business_address": "123 Craft Street, Lahore, Punjab",
  "website": "https://myartisanbrand.com",
  "social_media_links": {
    "facebook": "https://facebook.com/myartisanbrand",
    "instagram": "https://instagram.com/myartisanbrand"
  },
  "is_verified": false,
  "average_rating": "0.00",
  "total_feedbacks": 0,
  "created_at": "2025-10-27T19:30:00Z",
  "updated_at": "2025-10-27T19:30:00Z"
}
```

**Error (400 Bad Request):**

```json
{
  "non_field_errors": ["Only sellers can create seller profiles"]
}
```

```json
{
  "non_field_errors": ["Seller profile already exists"]
}
```

### Update Seller Profile

**Endpoint:** `PUT /api/seller-profiles/{id}/` or `PATCH /api/seller-profiles/{id}/`

**Authentication:** Required (Profile owner)

### Verify Seller (Admin Only)

**Endpoint:** `POST /api/seller-profiles/{id}/verify/`

**Authentication:** Required (Admin only)

**Response (200 OK):**

```json
{
  "message": "Seller verified successfully"
}
```

---

## Complaints

### Submit Complaint

**Endpoint:** `POST /api/complaints/`

**Authentication:** Required

**Request Body:**

```json
{
  "category": "seller",
  "subject": "Item not as described",
  "description": "The product quality is not as shown in pictures. The embroidery is poor and colors are faded.",
  "order": 1,
  "seller": 5
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| category | string | Yes | Complaint category |
| subject | string | Yes | Complaint subject |
| description | text | Yes | Detailed description |
| order | integer | No | Related order ID |
| seller | integer | No | Seller being complained about |

**Category Options:**
- `payment` - Payment Issue
- `seller` - Seller Issue
- `product` - Product Issue
- `platform` - Platform Issue
- `shipping` - Shipping Issue
- `other` - Other

**Response (201 Created):**

```json
{
  "id": 1,
  "complaint_number": "CMP-A1B2C3D4E5F6",
  "user": 1,
  "user_username": "buyer1",
  "category": "seller",
  "subject": "Item not as described",
  "description": "The product quality is not as shown in pictures. The embroidery is poor and colors are faded.",
  "order": 1,
  "order_number": "FXD-A1B2C3D4E5F6",
  "seller": 5,
  "seller_username": "seller1",
  "status": "open",
  "created_at": "2025-10-27T19:30:00Z",
  "updated_at": "2025-10-27T19:30:00Z"
}
```

### List My Complaints

**Endpoint:** `GET /api/complaints/`

**Authentication:** Required

**Response (200 OK):**

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "complaint_number": "CMP-A1B2C3D4E5F6",
      "user": 1,
      "user_username": "buyer1",
      "category": "seller",
      "subject": "Item not as described",
      "description": "The product quality is not as shown in pictures.",
      "order": 1,
      "order_number": "FXD-A1B2C3D4E5F6",
      "seller": 5,
      "seller_username": "seller1",
      "status": "open",
      "created_at": "2025-10-27T19:30:00Z",
      "updated_at": "2025-10-27T19:30:00Z"
    }
  ]
}
```

### Get Complaint Details

**Endpoint:** `GET /api/complaints/{id}/`

**Authentication:** Required (Complaint owner)

---

**End of Additional Features API Documentation**
