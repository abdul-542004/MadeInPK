# Seller Earnings API Documentation

This document describes the API endpoints for seller earnings, transactions, and product performance tracking.

## Base URL
```
/api/seller/
```

## Authentication
All endpoints require authentication with a valid token. The user must have seller role (`seller` or `both`).

Include the token in the header:
```
Authorization: Token <your-token>
```

---

## Endpoints

### 1. Get Seller Earnings Overview

Get comprehensive earnings data including current month, last month, total earnings, pending payouts, and historical data.

**Endpoint:** `GET /api/seller/earnings/`

**Response:**
```json
{
  "current_month": "45200.00",
  "last_month": "38300.00",
  "total_earnings": "234500.00",
  "pending_payouts": "12500.00",
  "earnings_by_month": [
    {
      "month": "Jan 2025",
      "amount": "35200.00",
      "earnings": 35200.0
    },
    {
      "month": "Feb 2025",
      "amount": "38300.00",
      "earnings": 38300.0
    },
    ...
  ],
  "earnings_by_week": [
    {
      "name": "Week 1",
      "amount": "8500.00",
      "earnings": 8500.0
    },
    {
      "name": "Week 2",
      "amount": "12300.00",
      "earnings": 12300.0
    },
    ...
  ],
  "earnings_by_quarter": [
    {
      "name": "Jan",
      "amount": "35200.00",
      "earnings": 35200.0
    },
    {
      "name": "Apr",
      "amount": "42100.00",
      "earnings": 42100.0
    },
    ...
  ],
  "earnings_by_year": [
    {
      "name": "2024",
      "amount": "180000.00",
      "earnings": 180000.0
    },
    {
      "name": "2025",
      "amount": "234500.00",
      "earnings": 234500.0
    },
    ...
  ]
}
```

**Response Fields:**

- `current_month` (string): Total earnings for the current month
- `last_month` (string): Total earnings for the previous month
- `total_earnings` (string): Total lifetime earnings
- `pending_payouts` (string): Earnings from paid/shipped orders not yet delivered
- `earnings_by_month` (array): Monthly earnings for the last 12 months
  - `month` (string): Month name and year
  - `amount` (string): Earnings amount as string
  - `earnings` (number): Earnings amount as number (for charts)
- `earnings_by_week` (array): Weekly earnings for the last 4 weeks
- `earnings_by_quarter` (array): Quarterly earnings for the last 4 quarters
- `earnings_by_year` (array): Yearly earnings for the last 5 years

**Notes:**
- All earnings include both single-seller orders and multi-seller cart orders
- Platform fee (2%) is already deducted from the amounts
- Only includes orders with status: `paid`, `shipped`, or `delivered`
- Pending payouts include only `paid` and `shipped` orders (not yet delivered)

---

### 2. Get Seller Transactions

Get detailed transaction history for the seller.

**Endpoint:** `GET /api/seller/transactions/`

**Query Parameters:**
- `limit` (optional, default: 50): Maximum number of transactions to return
- `offset` (optional, default: 0): Number of transactions to skip (for pagination)

**Example Request:**
```
GET /api/seller/transactions/?limit=20&offset=0
```

**Response:**
```json
{
  "transactions": [
    {
      "id": "TXN-ORD-2025-048",
      "description": "Order ORD-2025-048 - Hand-Embroidered Shawl",
      "date": "Oct 24, 2025",
      "amount": "+7,000",
      "status": "Pending",
      "status_color": "bg-amber-100 text-amber-700",
      "order_id": 123
    },
    {
      "id": "TXN-ORD-2025-047",
      "description": "Order ORD-2025-047 - Blue Pottery Vase Set",
      "date": "Oct 23, 2025",
      "amount": "+2,800",
      "status": "Completed",
      "status_color": "bg-emerald-100 text-emerald-700",
      "order_id": 122
    },
    ...
  ],
  "total": 156,
  "limit": 20,
  "offset": 0
}
```

**Response Fields:**

- `transactions` (array): List of transaction objects
  - `id` (string): Unique transaction identifier
  - `description` (string): Transaction description (order number and product name)
  - `date` (string): Transaction date (formatted as "Mon DD, YYYY")
  - `amount` (string): Transaction amount with sign (e.g., "+7,000")
  - `status` (string): Transaction status
    - `Pending`: Paid or shipped (awaiting delivery)
    - `Completed`: Delivered
    - `Cancelled`: Order cancelled
  - `status_color` (string): Tailwind CSS classes for status badge color
    - Pending: `bg-amber-100 text-amber-700`
    - Completed: `bg-emerald-100 text-emerald-700`
    - Cancelled: `bg-red-100 text-red-700`
  - `order_id` (number): Associated order ID
- `total` (number): Total number of transactions
- `limit` (number): Requested limit
- `offset` (number): Requested offset

**Notes:**
- Transactions are sorted by date (newest first)
- Includes both single-seller and multi-seller order transactions
- Amount is formatted with comma separators and no decimals

---

### 3. Get Product Performance

Get sales performance statistics for seller's products.

**Endpoint:** `GET /api/seller/product-performance/`

**Response:**
```json
{
  "products": [
    {
      "name": "Hand-Embroidered Shawl",
      "sales": 45,
      "revenue": "315000.00"
    },
    {
      "name": "Blue Pottery Vase",
      "sales": 32,
      "revenue": "89600.00"
    },
    {
      "name": "Traditional Jewelry Set",
      "sales": 38,
      "revenue": "209000.00"
    },
    {
      "name": "Brass Metalwork",
      "sales": 28,
      "revenue": "159600.00"
    },
    {
      "name": "Handwoven Carpet",
      "sales": 15,
      "revenue": "187500.00"
    }
  ]
}
```

**Response Fields:**

- `products` (array): List of product performance objects (top 10 products by sales)
  - `name` (string): Product name
  - `sales` (number): Total number of units sold
  - `revenue` (string): Total revenue from this product

**Notes:**
- Only includes delivered orders
- Products are sorted by sales count (highest first)
- Limited to top 10 products
- Revenue includes platform fee deduction (2%)
- Combines sales from both single-seller and multi-seller orders

---

### 4. Get Seller Statistics (Legacy)

Get basic seller statistics for dashboard overview.

**Endpoint:** `GET /api/seller/statistics/`

**Response:**
```json
{
  "total_sales": 156,
  "total_orders": 203,
  "pending_orders": 12,
  "total_revenue": "234500.00",
  "total_products": 45,
  "active_auctions": 8
}
```

**Response Fields:**

- `total_sales` (number): Total delivered orders
- `total_orders` (number): Total orders (all statuses)
- `pending_orders` (number): Orders paid but not yet shipped
- `total_revenue` (string): Total revenue from paid/shipped/delivered orders
- `total_products` (number): Total products created by seller
- `active_auctions` (number): Active auction listings

**Notes:**
- This is a legacy endpoint, consider using `/api/seller/earnings/` for more detailed data
- Only includes single-seller orders (not multi-seller cart orders)

---

## Error Responses

### 403 Forbidden
User is not a seller.

```json
{
  "error": "Only sellers can access this endpoint"
}
```

### 401 Unauthorized
No authentication token provided or invalid token.

```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Frontend Integration Example

### React/TypeScript Example

```typescript
import { useState, useEffect } from "react";
import axios from "axios";

interface EarningsData {
  current_month: string;
  last_month: string;
  total_earnings: string;
  pending_payouts: string;
  earnings_by_month: Array<{
    month: string;
    amount: string;
    earnings: number;
  }>;
  earnings_by_week: Array<{
    name: string;
    amount: string;
    earnings: number;
  }>;
}

export function SellerEarnings() {
  const [earningsData, setEarningsData] = useState<EarningsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEarnings();
  }, []);

  const loadEarnings = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await axios.get('/api/seller/earnings/', {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      setEarningsData(response.data);
    } catch (error) {
      console.error('Error loading earnings:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!earningsData) return <div>No data available</div>;

  return (
    <div>
      <h1>Earnings Overview</h1>
      <p>Current Month: PKR {parseFloat(earningsData.current_month).toLocaleString()}</p>
      <p>Total Earnings: PKR {parseFloat(earningsData.total_earnings).toLocaleString()}</p>
      {/* Render charts using earnings_by_month, etc. */}
    </div>
  );
}
```

### Axios Service Example

```typescript
// sellerService.ts
import axios from 'axios';

const API_BASE_URL = '/api/seller';

export const sellerService = {
  async getSellerEarnings() {
    const token = localStorage.getItem('authToken');
    const response = await axios.get(`${API_BASE_URL}/earnings/`, {
      headers: { 'Authorization': `Token ${token}` }
    });
    return response.data;
  },

  async getSellerTransactions(limit = 50, offset = 0) {
    const token = localStorage.getItem('authToken');
    const response = await axios.get(`${API_BASE_URL}/transactions/`, {
      params: { limit, offset },
      headers: { 'Authorization': `Token ${token}` }
    });
    return response.data;
  },

  async getProductPerformance() {
    const token = localStorage.getItem('authToken');
    const response = await axios.get(`${API_BASE_URL}/product-performance/`, {
      headers: { 'Authorization': `Token ${token}` }
    });
    return response.data;
  }
};
```

---

## Chart Data Format

The API provides data in formats compatible with popular charting libraries like Recharts.

### For Line/Bar Charts (Monthly/Weekly/Quarterly/Yearly)

```typescript
// Direct usage with Recharts
<LineChart data={earningsData.earnings_by_month}>
  <XAxis dataKey="month" />
  <YAxis />
  <Line dataKey="earnings" />
</LineChart>
```

### For Product Performance Bar Chart

```typescript
<BarChart data={productPerformance.products}>
  <XAxis dataKey="name" />
  <YAxis />
  <Bar dataKey="sales" />
</BarChart>
```

---

## Rate Limiting

No specific rate limits are enforced, but please use reasonable request intervals to avoid overloading the server.

---

## Changelog

### Version 1.0 (November 2025)
- Initial release
- Added `/earnings/` endpoint
- Added `/transactions/` endpoint
- Added `/product-performance/` endpoint
- Support for multi-seller cart orders
- Historical data for week, month, quarter, and year

---

## Support

For issues or questions, please contact the development team or create an issue in the project repository.
