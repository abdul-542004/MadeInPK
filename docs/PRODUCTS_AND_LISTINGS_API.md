# MadeInPK Products & Listings API

**Base URL:** `http://localhost:8000/api/`

---

## Table of Contents

1. [Categories](#categories)
2. [Products](#products)
3. [Auction Listings](#auction-listings)
4. [Fixed Price Listings](#fixed-price-listings)

---

## Categories

### List All Categories

**Endpoint:** `GET /api/categories/`

**Authentication:** Not required

**Response (200 OK):**

```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Textiles",
      "description": "Fabrics, clothing, and textile products",
      "parent": null,
      "subcategories": []
    },
    {
      "id": 2,
      "name": "Handicrafts",
      "description": "Handmade decorative items and crafts",
      "parent": null,
      "subcategories": []
    },
    {
      "id": 3,
      "name": "Pottery",
      "description": "Ceramic and pottery items",
      "parent": null,
      "subcategories": []
    },
    {
      "id": 4,
      "name": "Jewelry",
      "description": "Traditional and contemporary jewelry",
      "parent": null,
      "subcategories": []
    },
    {
      "id": 5,
      "name": "Home Decor",
      "description": "Home decoration and furnishing items",
      "parent": null,
      "subcategories": []
    },
    {
      "id": 6,
      "name": "Carpets",
      "description": "Handwoven carpets and rugs",
      "parent": null,
      "subcategories": []
    },
    {
      "id": 7,
      "name": "Leather Goods",
      "description": "Leather products and accessories",
      "parent": null,
      "subcategories": []
    },
    {
      "id": 8,
      "name": "Woodwork",
      "description": "Wooden furniture and carvings",
      "parent": null,
      "subcategories": []
    }
  ]
}
```

---

## Products

### List Products

**Endpoint:** `GET /api/products/`

**Authentication:** Not required

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| seller | integer | Filter by seller ID | `?seller=5` |
| category | integer | Filter by category ID | `?category=1` |
| condition | string | Filter by condition | `?condition=new` |
| search | string | Search in name/description | `?search=shawl` |
| ordering | string | Sort field | `?ordering=-created_at` |
| page | integer | Page number | `?page=2` |
| page_size | integer | Items per page (max 100) | `?page_size=20` |

**Condition Options:** `new`, `like_new`, `good`, `fair`

**Ordering Options:** `created_at`, `-created_at`, `name`, `-name`

**Example Request:**

```
GET /api/products/?category=1&ordering=-created_at&page=1
```

**Response (200 OK):**

```json
{
  "count": 11,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "seller": 5,
      "seller_username": "seller1",
      "category": 1,
      "category_name": "Textiles",
      "name": "Handwoven Pashmina Shawl",
      "description": "Exquisite handwoven pashmina shawl from Kashmir, featuring traditional paisley patterns. Made from the finest cashmere wool, perfect for special occasions.",
      "condition": "new",
      "images": [
        {
          "id": 1,
          "image": "/media/products/pashmina_shawl.jpg",
          "image_url": "http://localhost:8000/media/products/pashmina_shawl.jpg",
          "is_primary": true,
          "order": 0
        }
      ],
      "listing_type": "auction",
      "average_rating": null,
      "total_reviews": 0,
      "seller_profile": {
        "brand_name": "Hassan Textiles",
        "biography": "Family-owned textile business for 3 generations, specializing in handwoven fabrics.",
        "is_verified": true,
        "average_rating": "4.70"
      },
      "created_at": "2025-10-20T10:00:00Z",
      "updated_at": "2025-10-20T10:00:00Z"
    },
    {
      "id": 2,
      "seller": 5,
      "seller_username": "seller1",
      "category": 1,
      "category_name": "Textiles",
      "name": "Embroidered Cotton Kurti",
      "description": "Beautiful hand-embroidered cotton kurti with mirror work and traditional motifs. Comfortable for everyday wear.",
      "condition": "new",
      "images": [
        {
          "id": 2,
          "image": "/media/products/embroidered_kurti.jpg",
          "image_url": "http://localhost:8000/media/products/embroidered_kurti.jpg",
          "is_primary": true,
          "order": 0
        }
      ],
      "listing_type": "fixed_price",
      "average_rating": 4.5,
      "total_reviews": 2,
      "seller_profile": {
        "brand_name": "Hassan Textiles",
        "biography": "Family-owned textile business for 3 generations, specializing in handwoven fabrics.",
        "is_verified": true,
        "average_rating": "4.70"
      },
      "created_at": "2025-10-20T10:00:00Z",
      "updated_at": "2025-10-20T10:00:00Z"
    }
  ]
}
```

### Get Product Details

**Endpoint:** `GET /api/products/{id}/`

**Authentication:** Not required

**Example:** `GET /api/products/1/`

**Response (200 OK):**

```json
{
  "id": 1,
  "seller": 5,
  "seller_username": "seller1",
  "category": 1,
  "category_name": "Textiles",
  "name": "Handwoven Pashmina Shawl",
  "description": "Exquisite handwoven pashmina shawl from Kashmir, featuring traditional paisley patterns. Made from the finest cashmere wool, perfect for special occasions.",
  "condition": "new",
  "images": [
    {
      "id": 1,
      "image": "/media/products/pashmina_shawl.jpg",
      "image_url": "http://localhost:8000/media/products/pashmina_shawl.jpg",
      "is_primary": true,
      "order": 0
    }
  ],
  "listing_type": "auction",
  "average_rating": null,
  "total_reviews": 0,
  "seller_profile": {
    "brand_name": "Hassan Textiles",
    "biography": "Family-owned textile business for 3 generations, specializing in handwoven fabrics.",
    "is_verified": true,
    "average_rating": "4.70"
  },
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-20T10:00:00Z"
}
```

### Create Product

**Endpoint:** `POST /api/products/`

**Authentication:** Required (Seller role)

**Content-Type:** `multipart/form-data`

**Form Data:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| category | integer | Yes | Category ID |
| name | string | Yes | Product name |
| description | text | Yes | Product description |
| condition | string | Yes | Product condition |
| images | file[] | No | Product images (multiple) |

**Example Request (using FormData):**

```javascript
const formData = new FormData();
formData.append('category', 1);
formData.append('name', 'Traditional Ajrak Shawl');
formData.append('description', 'Authentic Sindhi Ajrak with block printing');
formData.append('condition', 'new');
formData.append('images', file1);
formData.append('images', file2);

const response = await axios.post(
  'http://localhost:8000/api/products/',
  formData,
  {
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'multipart/form-data'
    }
  }
);
```

**Response (201 Created):**

```json
{
  "id": 12,
  "seller": 5,
  "seller_username": "seller1",
  "category": 1,
  "category_name": "Textiles",
  "name": "Traditional Ajrak Shawl",
  "description": "Authentic Sindhi Ajrak with block printing",
  "condition": "new",
  "images": [
    {
      "id": 15,
      "image": "/media/products/ajrak_1.jpg",
      "image_url": "http://localhost:8000/media/products/ajrak_1.jpg",
      "is_primary": true,
      "order": 0
    },
    {
      "id": 16,
      "image": "/media/products/ajrak_2.jpg",
      "image_url": "http://localhost:8000/media/products/ajrak_2.jpg",
      "is_primary": false,
      "order": 1
    }
  ],
  "listing_type": null,
  "average_rating": null,
  "total_reviews": 0,
  "seller_profile": {
    "brand_name": "Hassan Textiles",
    "biography": "Family-owned textile business for 3 generations, specializing in handwoven fabrics.",
    "is_verified": true,
    "average_rating": "4.70"
  },
  "created_at": "2025-10-27T19:00:00Z",
  "updated_at": "2025-10-27T19:00:00Z"
}
```

### Add Image to Product

**Endpoint:** `POST /api/products/{id}/add_image/`

**Authentication:** Required (Product owner only)

**Content-Type:** `multipart/form-data`

**Form Data:**

| Field | Type | Required |
|-------|------|----------|
| image | file | Yes |

**Response (201 Created):**

```json
{
  "id": 17,
  "image": "/media/products/ajrak_3.jpg",
  "image_url": "http://localhost:8000/media/products/ajrak_3.jpg",
  "is_primary": false,
  "order": 2
}
```

**Error (403 Forbidden):**

```json
{
  "error": "You can only add images to your own products"
}
```

### Update Product

**Endpoint:** `PUT /api/products/{id}/` or `PATCH /api/products/{id}/`

**Authentication:** Required (Product owner only)

### Delete Product

**Endpoint:** `DELETE /api/products/{id}/`

**Authentication:** Required (Product owner only)

---

## Auction Listings

### List Auctions

**Endpoint:** `GET /api/auctions/`

**Authentication:** Not required

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| status | string | Filter by status | `?status=active` |
| seller | integer | Filter by seller ID | `?seller=5` |
| category | integer | Filter by category ID | `?category=1` |
| search | string | Search in product name/description | `?search=shawl` |
| ordering | string | Sort field | `?ordering=end_time` |

**Status Options:** `active`, `ended`, `cancelled`, `completed`

**Ordering Options:** `end_time`, `-end_time`, `current_price`, `-current_price`, `created_at`, `-created_at`

**Example:** `GET /api/auctions/?status=active&ordering=end_time`

**Response (200 OK):**

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "seller": 5,
        "seller_username": "seller1",
        "category": 1,
        "category_name": "Textiles",
        "name": "Handwoven Pashmina Shawl",
        "description": "Exquisite handwoven pashmina shawl from Kashmir...",
        "condition": "new",
        "images": [
          {
            "id": 1,
            "image": "/media/products/pashmina_shawl.jpg",
            "image_url": "http://localhost:8000/media/products/pashmina_shawl.jpg",
            "is_primary": true,
            "order": 0
          }
        ],
        "listing_type": "auction",
        "seller_profile": {
          "brand_name": "Hassan Textiles",
          "is_verified": true,
          "average_rating": "4.70"
        }
      },
      "starting_price": "2500.00",
      "current_price": "2875.00",
      "start_time": "2025-10-27T18:00:00Z",
      "end_time": "2025-10-29T18:00:00Z",
      "status": "active",
      "winner": null,
      "winner_username": null,
      "latest_bids": [
        {
          "id": 5,
          "bidder": 2,
          "bidder_username": "buyer2",
          "amount": "2875.00",
          "bid_time": "2025-10-27T18:32:00Z",
          "is_winning": true
        },
        {
          "id": 4,
          "bidder": 1,
          "bidder_username": "buyer1",
          "amount": "2750.00",
          "bid_time": "2025-10-27T18:15:00Z",
          "is_winning": false
        }
      ],
      "total_bids": 5,
      "time_remaining": 172800.0,
      "created_at": "2025-10-20T10:00:00Z"
    }
  ]
}
```

### Get Auction Details

**Endpoint:** `GET /api/auctions/{id}/`

**Authentication:** Not required

**Example:** `GET /api/auctions/1/`

### Create Auction

**Endpoint:** `POST /api/auctions/`

**Authentication:** Required (Seller role, product owner)

**Request Body:**

```json
{
  "product_id": 12,
  "starting_price": 5000.00,
  "start_time": "2025-10-28T10:00:00Z",
  "end_time": "2025-10-30T10:00:00Z"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| product_id | integer | Yes | ID of product to auction |
| starting_price | decimal | Yes | Starting bid price (min 0.01) |
| start_time | datetime | Yes | Auction start time (ISO 8601) |
| end_time | datetime | Yes | Auction end time (ISO 8601) |

**Validation Rules:**
- Product must exist and belong to the user
- Product must not already have a listing (auction or fixed price)
- End time must be after start time
- Starting price must be positive

**Response (201 Created):**

```json
{
  "id": 7,
  "product": {
    "id": 12,
    "name": "Traditional Ajrak Shawl",
    "seller_username": "seller1"
  },
  "starting_price": "5000.00",
  "current_price": "5000.00",
  "start_time": "2025-10-28T10:00:00Z",
  "end_time": "2025-10-30T10:00:00Z",
  "status": "active",
  "winner": null,
  "latest_bids": [],
  "total_bids": 0,
  "time_remaining": 172800.0,
  "created_at": "2025-10-27T19:00:00Z"
}
```

**Error (400 Bad Request):**

```json
{
  "product_id": ["Product already has a listing"],
  "end_time": ["End time must be after start time"]
}
```

### Place Bid (REST API)

**Endpoint:** `POST /api/auctions/{id}/place_bid/`

**Authentication:** Required

**Request Body:**

```json
{
  "amount": 3000.00
}
```

**Response (201 Created):**

```json
{
  "id": 15,
  "bidder": 1,
  "bidder_username": "buyer1",
  "amount": "3000.00",
  "bid_time": "2025-10-27T19:00:00Z",
  "is_winning": true
}
```

**Error Responses:**

```json
{
  "error": "Auction is not active"
}
```

```json
{
  "error": "Your account is blocked"
}
```

```json
{
  "error": "You cannot bid on your own auction"
}
```

```json
{
  "amount": ["Bid must be higher than current price of 2875.00"]
}
```

### Get Auction Bids

**Endpoint:** `GET /api/auctions/{id}/bids/`

**Authentication:** Not required

**Response (200 OK):**

```json
[
  {
    "id": 5,
    "bidder": 2,
    "bidder_username": "buyer2",
    "amount": "2875.00",
    "bid_time": "2025-10-27T18:32:00Z",
    "is_winning": true
  },
  {
    "id": 4,
    "bidder": 1,
    "bidder_username": "buyer1",
    "amount": "2750.00",
    "bid_time": "2025-10-27T18:15:00Z",
    "is_winning": false
  },
  {
    "id": 3,
    "bidder": 3,
    "bidder_username": "buyer3",
    "amount": "2625.00",
    "bid_time": "2025-10-27T18:00:00Z",
    "is_winning": false
  }
]
```

---

## Fixed Price Listings

### List Fixed Price Listings

**Endpoint:** `GET /api/listings/`

**Authentication:** Not required

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| status | string | Filter by status | `?status=active` |
| seller | integer | Filter by seller ID | `?seller=5` |
| category | integer | Filter by category ID | `?category=1` |
| min_price | decimal | Minimum price | `?min_price=1000` |
| max_price | decimal | Maximum price | `?max_price=5000` |
| featured | boolean | Featured listings only | `?featured=true` |
| search | string | Search query | `?search=kurti` |
| ordering | string | Sort field | `?ordering=price` |

**Status Options:** `active`, `inactive`, `out_of_stock`

**Ordering Options:** `price`, `-price`, `created_at`, `-created_at`

**Example:** `GET /api/listings/?status=active&min_price=1000&max_price=5000`

**Response (200 OK):**

```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product": {
        "id": 2,
        "seller": 5,
        "seller_username": "seller1",
        "category": 1,
        "category_name": "Textiles",
        "name": "Embroidered Cotton Kurti",
        "description": "Beautiful hand-embroidered cotton kurti with mirror work and traditional motifs. Comfortable for everyday wear.",
        "condition": "new",
        "images": [
          {
            "id": 2,
            "image": "/media/products/embroidered_kurti.jpg",
            "image_url": "http://localhost:8000/media/products/embroidered_kurti.jpg",
            "is_primary": true,
            "order": 0
          }
        ],
        "listing_type": "fixed_price",
        "average_rating": 4.5,
        "total_reviews": 2,
        "seller_profile": {
          "brand_name": "Hassan Textiles",
          "is_verified": true,
          "average_rating": "4.70"
        }
      },
      "price": "1200.00",
      "quantity": 5,
      "status": "active",
      "featured": false,
      "created_at": "2025-10-20T10:00:00Z",
      "updated_at": "2025-10-20T10:00:00Z"
    },
    {
      "id": 2,
      "product": {
        "id": 4,
        "seller": 6,
        "seller_username": "seller2",
        "category": 2,
        "category_name": "Handicrafts",
        "name": "Brass Wall Hanging",
        "description": "Intricately designed brass wall hanging with traditional Islamic calligraphy. Handcrafted by skilled artisans.",
        "condition": "new",
        "images": [
          {
            "id": 4,
            "image": "/media/products/brass_wall_hanging.jpg",
            "image_url": "http://localhost:8000/media/products/brass_wall_hanging.jpg",
            "is_primary": true,
            "order": 0
          }
        ],
        "listing_type": "fixed_price",
        "average_rating": null,
        "total_reviews": 0,
        "seller_profile": {
          "brand_name": "Ayesha Crafts",
          "is_verified": true,
          "average_rating": "4.80"
        }
      },
      "price": "3200.00",
      "quantity": 3,
      "status": "active",
      "featured": false,
      "created_at": "2025-10-20T10:00:00Z",
      "updated_at": "2025-10-20T10:00:00Z"
    }
  ]
}
```

### Get Fixed Price Listing Details

**Endpoint:** `GET /api/listings/{id}/`

**Authentication:** Not required

### Create Fixed Price Listing

**Endpoint:** `POST /api/listings/`

**Authentication:** Required (Seller role, product owner)

**Request Body:**

```json
{
  "product_id": 12,
  "price": 1500.00,
  "quantity": 10,
  "featured": false
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| product_id | integer | Yes | ID of product to list |
| price | decimal | Yes | Listing price (min 0.01) |
| quantity | integer | Yes | Available quantity (min 1) |
| featured | boolean | No | Mark as featured (default: false) |

**Response (201 Created):**

```json
{
  "id": 8,
  "product": {
    "id": 12,
    "name": "Traditional Ajrak Shawl",
    "seller_username": "seller1"
  },
  "price": "1500.00",
  "quantity": 10,
  "status": "active",
  "featured": false,
  "created_at": "2025-10-27T19:00:00Z",
  "updated_at": "2025-10-27T19:00:00Z"
}
```

### Purchase Fixed Price Item

**Endpoint:** `POST /api/listings/{id}/purchase/`

**Authentication:** Required

**Request Body:**

```json
{
  "quantity": 2,
  "shipping_address": 1
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| quantity | integer | Yes | Quantity to purchase (min 1) |
| shipping_address | integer | Yes | Address ID for shipping |

**Response (201 Created):**

```json
{
  "id": 10,
  "order_number": "FXD-A1B2C3D4E5F6",
  "buyer": 1,
  "buyer_username": "buyer1",
  "seller": 5,
  "seller_username": "seller1",
  "product": 2,
  "product_name": "Embroidered Cotton Kurti",
  "order_type": "fixed_price",
  "quantity": 2,
  "unit_price": "1200.00",
  "total_amount": "2400.00",
  "platform_fee": "48.00",
  "seller_amount": "2352.00",
  "shipping_address": 1,
  "shipping_address_detail": {
    "street_address": "456 Main Street",
    "city_name": "Lahore",
    "province_name": "Punjab",
    "postal_code": "54000"
  },
  "status": "pending_payment",
  "payment_url": "http://localhost:8000/api/payments/10/checkout/",
  "payment_deadline": "2025-10-28T19:00:00Z",
  "created_at": "2025-10-27T19:00:00Z"
}
```

**Error Responses:**

```json
{
  "error": "Listing is not active"
}
```

```json
{
  "error": "Not enough quantity available"
}
```

```json
{
  "error": "You cannot purchase your own listing"
}
```

---

## Sample Data Reference

### Sample Products

| ID | Name | Category | Seller | Type |
|----|------|----------|--------|------|
| 1 | Handwoven Pashmina Shawl | Textiles | seller1 | Auction |
| 2 | Embroidered Cotton Kurti | Textiles | seller1 | Fixed Price |
| 3 | Silk Bedspread Set | Textiles | seller1 | Auction |
| 4 | Brass Wall Hanging | Handicrafts | seller2 | Fixed Price |
| 5 | Wooden Jewelry Box | Handicrafts | seller2 | Auction |
| 6 | Blue Pottery Vase | Pottery | seller3 | Fixed Price |
| 7 | Ceramic Dinner Set | Pottery | seller3 | Auction |
| 8 | Silver Enamel Necklace | Jewelry | seller4 | Fixed Price |
| 9 | Gold-Plated Earrings Set | Jewelry | seller4 | Auction |
| 10 | Kashmiri Silk Carpet | Carpets | seller1 | Auction |
| 11 | Sheesham Wood Dining Table | Woodwork | seller2 | Fixed Price |

---

**End of Products & Listings API Documentation**
