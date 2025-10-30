# MadeInPK Orders & Payments API

**Base URL:** `http://localhost:8000/api/`

---

## Table of Contents

1. [Orders](#orders)
2. [Order Management](#order-management)
3. [Payment Flow](#payment-flow)

---

## Orders

### List Orders

**Endpoint:** `GET /api/orders/`

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| status | string | Filter by order status | `?status=paid` |
| role | string | Filter by user role | `?role=buyer` |
| ordering | string | Sort field | `?ordering=-created_at` |

**Status Options:**
- `pending_payment` - Awaiting payment
- `payment_failed` - Payment failed
- `paid` - Payment successful
- `shipped` - Order shipped
- `delivered` - Order delivered
- `cancelled` - Order cancelled

**Role Options:**
- `buyer` - Orders where you are the buyer
- `seller` - Orders where you are the seller

**Ordering Options:** `created_at`, `-created_at`, `status`

**Example:** `GET /api/orders/?role=buyer&status=paid`

**Response (200 OK):**

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
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
        "id": 1,
        "street_address": "456 Main Street",
        "city": 1,
        "city_name": "Lahore",
        "province_name": "Punjab",
        "postal_code": "54000",
        "is_default": true
      },
      "status": "paid",
      "payment_url": "http://localhost:8000/api/payments/1/checkout/",
      "payment_deadline": "2025-10-28T19:00:00Z",
      "created_at": "2025-10-27T18:00:00Z",
      "paid_at": "2025-10-27T18:30:00Z",
      "shipped_at": null,
      "delivered_at": null
    },
    {
      "id": 2,
      "order_number": "AUC-B2C3D4E5F6G7",
      "buyer": 1,
      "buyer_username": "buyer1",
      "seller": 6,
      "seller_username": "seller2",
      "product": 5,
      "product_name": "Wooden Jewelry Box",
      "order_type": "auction",
      "quantity": 1,
      "unit_price": "2100.00",
      "total_amount": "2100.00",
      "platform_fee": "42.00",
      "seller_amount": "2058.00",
      "shipping_address": 1,
      "shipping_address_detail": {
        "id": 1,
        "street_address": "456 Main Street",
        "city": 1,
        "city_name": "Lahore",
        "province_name": "Punjab",
        "postal_code": "54000",
        "is_default": true
      },
      "status": "shipped",
      "payment_url": "",
      "payment_deadline": "2025-10-26T10:00:00Z",
      "created_at": "2025-10-25T10:00:00Z",
      "paid_at": "2025-10-25T11:00:00Z",
      "shipped_at": "2025-10-26T14:00:00Z",
      "delivered_at": null
    }
  ]
}
```

### Get Order Details

**Endpoint:** `GET /api/orders/{id}/`

**Authentication:** Required (Buyer or Seller of the order)

**Example:** `GET /api/orders/1/`

**Response (200 OK):**

```json
{
  "id": 1,
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
    "id": 1,
    "street_address": "456 Main Street",
    "city": 1,
    "city_name": "Lahore",
    "province_name": "Punjab",
    "postal_code": "54000",
    "is_default": true
  },
  "status": "paid",
  "payment_url": "http://localhost:8000/api/payments/1/checkout/",
  "payment_deadline": "2025-10-28T19:00:00Z",
  "created_at": "2025-10-27T18:00:00Z",
  "paid_at": "2025-10-27T18:30:00Z",
  "shipped_at": null,
  "delivered_at": null
}
```

---

## Order Management

### Mark Order as Shipped

**Endpoint:** `POST /api/orders/{id}/mark_shipped/`

**Authentication:** Required (Seller only)

**Description:** Seller marks order as shipped after dispatching the item.

**Requirements:**
- User must be the seller of the order
- Order status must be `paid`

**Response (200 OK):**

```json
{
  "message": "Order marked as shipped"
}
```

**Error Responses:**

**403 Forbidden:**
```json
{
  "error": "Only seller can mark as shipped"
}
```

**400 Bad Request:**
```json
{
  "error": "Order must be paid first"
}
```

**Example:**

```javascript
const response = await axios.post(
  `http://localhost:8000/api/orders/1/mark_shipped/`,
  {},
  {
    headers: {
      'Authorization': `Token ${token}`
    }
  }
);
```

**Side Effects:**
- Order status changes to `shipped`
- `shipped_at` timestamp is set
- Buyer receives notification about shipment

---

### Mark Order as Delivered

**Endpoint:** `POST /api/orders/{id}/mark_delivered/`

**Authentication:** Required (Buyer only)

**Description:** Buyer confirms receipt of the item.

**Requirements:**
- User must be the buyer of the order
- Order status must be `shipped`

**Response (200 OK):**

```json
{
  "message": "Order marked as delivered"
}
```

**Error Responses:**

**403 Forbidden:**
```json
{
  "error": "Only buyer can mark as delivered"
}
```

**400 Bad Request:**
```json
{
  "error": "Order must be shipped first"
}
```

**Example:**

```javascript
const response = await axios.post(
  `http://localhost:8000/api/orders/1/mark_delivered/`,
  {},
  {
    headers: {
      'Authorization': `Token ${token}`
    }
  }
);
```

**Side Effects:**
- Order status changes to `delivered`
- `delivered_at` timestamp is set
- Seller receives notification about delivery
- Buyer receives notification requesting feedback

---

## Payment Flow

### Overview

MadeInPK uses Stripe for payment processing. The payment flow is:

1. **Order Creation** - Order is created with `pending_payment` status
2. **Payment Processing** - Buyer completes payment via Stripe
3. **Payment Confirmation** - Webhook confirms payment, order status → `paid`
4. **Shipping** - Seller ships item, status → `shipped`
5. **Delivery** - Buyer confirms delivery, status → `delivered`
6. **Payout** - Platform transfers funds to seller (minus 2% fee)

### Payment Deadline

- **Fixed Price Orders:** 24 hours from order creation
- **Auction Orders:** 24 hours from auction end

If payment is not completed within deadline:
- Order status → `payment_failed`
- User's `failed_payment_count` increments
- After 3 failed payments, account is blocked

### Platform Fee

MadeInPK charges a **2% platform fee** on all transactions:

```
Platform Fee = Total Amount × 0.02
Seller Amount = Total Amount - Platform Fee
```

**Example:**
- Total Amount: PKR 2,400
- Platform Fee: PKR 48 (2%)
- Seller Receives: PKR 2,352

### Payment URL

After order creation, use the `payment_url` to redirect buyer to Stripe checkout:

```json
{
  "payment_url": "http://localhost:8000/api/payments/1/checkout/"
}
```

**Frontend Implementation:**

```javascript
// After creating order
const orderResponse = await axios.post(
  'http://localhost:8000/api/listings/1/purchase/',
  {
    quantity: 2,
    shipping_address: 1
  },
  {
    headers: { 'Authorization': `Token ${token}` }
  }
);

// Redirect to payment
window.location.href = orderResponse.data.payment_url;
```

---

## Order Status Flow

```
Fixed Price Purchase:
pending_payment → paid → shipped → delivered

Auction Win:
pending_payment → paid → shipped → delivered

Payment Failed:
pending_payment → payment_failed

Cancelled:
pending_payment → cancelled
```

### Status Descriptions

| Status | Description | Actions Available |
|--------|-------------|-------------------|
| `pending_payment` | Awaiting payment | Buyer: Complete payment |
| `payment_failed` | Payment failed or deadline passed | None |
| `paid` | Payment successful | Seller: Mark as shipped |
| `shipped` | Item shipped by seller | Buyer: Mark as delivered |
| `delivered` | Item received by buyer | Buyer: Leave feedback |
| `cancelled` | Order cancelled | None |

---

## Order Types

### Fixed Price Order

Created when buyer purchases a fixed price listing.

**Order Number Format:** `FXD-XXXXXXXXXXXX`

**Example:**
```json
{
  "order_number": "FXD-A1B2C3D4E5F6",
  "order_type": "fixed_price",
  "quantity": 2,
  "unit_price": "1200.00",
  "total_amount": "2400.00"
}
```

### Auction Order

Created when auction ends and winner is determined.

**Order Number Format:** `AUC-XXXXXXXXXXXX`

**Example:**
```json
{
  "order_number": "AUC-B2C3D4E5F6G7",
  "order_type": "auction",
  "quantity": 1,
  "unit_price": "2875.00",
  "total_amount": "2875.00"
}
```

---

## Complete Purchase Flow Example

### React Component Example

```javascript
import { useState } from 'react';
import axios from 'axios';

function PurchaseFlow({ listingId, price }) {
  const [quantity, setQuantity] = useState(1);
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('authToken');

  const handlePurchase = async () => {
    if (!selectedAddress) {
      alert('Please select a shipping address');
      return;
    }

    setLoading(true);

    try {
      // Create order
      const response = await axios.post(
        `http://localhost:8000/api/listings/${listingId}/purchase/`,
        {
          quantity: quantity,
          shipping_address: selectedAddress
        },
        {
          headers: {
            'Authorization': `Token ${token}`
          }
        }
      );

      const order = response.data;

      // Show order summary
      alert(`Order created: ${order.order_number}\nTotal: PKR ${order.total_amount}`);

      // Redirect to payment
      window.location.href = order.payment_url;

    } catch (error) {
      console.error('Purchase failed:', error);
      
      if (error.response?.data?.error) {
        alert(error.response.data.error);
      } else {
        alert('Purchase failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const totalAmount = (price * quantity).toFixed(2);
  const platformFee = (totalAmount * 0.02).toFixed(2);

  return (
    <div className="purchase-flow">
      <h2>Purchase Item</h2>
      
      {/* Quantity Selector */}
      <div className="quantity-selector">
        <label>Quantity:</label>
        <input
          type="number"
          min="1"
          value={quantity}
          onChange={(e) => setQuantity(parseInt(e.target.value))}
        />
      </div>

      {/* Address Selector */}
      <div className="address-selector">
        <label>Shipping Address:</label>
        <select
          value={selectedAddress || ''}
          onChange={(e) => setSelectedAddress(parseInt(e.target.value))}
        >
          <option value="">Select address...</option>
          {/* Populate with user's addresses */}
        </select>
      </div>

      {/* Order Summary */}
      <div className="order-summary">
        <h3>Order Summary</h3>
        <p>Unit Price: PKR {price}</p>
        <p>Quantity: {quantity}</p>
        <p>Subtotal: PKR {totalAmount}</p>
        <p>Platform Fee (2%): PKR {platformFee}</p>
        <p><strong>Total: PKR {totalAmount}</strong></p>
      </div>

      {/* Purchase Button */}
      <button
        onClick={handlePurchase}
        disabled={loading || !selectedAddress}
      >
        {loading ? 'Processing...' : 'Proceed to Payment'}
      </button>
    </div>
  );
}
```

### Seller Order Management

```javascript
function SellerOrderManagement({ orderId }) {
  const [order, setOrder] = useState(null);
  const token = localStorage.getItem('authToken');

  useEffect(() => {
    fetchOrder();
  }, [orderId]);

  const fetchOrder = async () => {
    const response = await axios.get(
      `http://localhost:8000/api/orders/${orderId}/`,
      {
        headers: { 'Authorization': `Token ${token}` }
      }
    );
    setOrder(response.data);
  };

  const markAsShipped = async () => {
    try {
      await axios.post(
        `http://localhost:8000/api/orders/${orderId}/mark_shipped/`,
        {},
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      
      alert('Order marked as shipped!');
      fetchOrder(); // Refresh order data
      
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to mark as shipped');
    }
  };

  if (!order) return <div>Loading...</div>;

  return (
    <div className="order-management">
      <h2>Order #{order.order_number}</h2>
      
      <div className="order-details">
        <p>Buyer: {order.buyer_username}</p>
        <p>Product: {order.product_name}</p>
        <p>Quantity: {order.quantity}</p>
        <p>Total: PKR {order.total_amount}</p>
        <p>Your Earnings: PKR {order.seller_amount}</p>
        <p>Status: <span className={`status-${order.status}`}>
          {order.status.toUpperCase()}
        </span></p>
      </div>

      <div className="shipping-address">
        <h3>Shipping Address</h3>
        <p>{order.shipping_address_detail.street_address}</p>
        <p>{order.shipping_address_detail.city_name}, {order.shipping_address_detail.province_name}</p>
        <p>Postal Code: {order.shipping_address_detail.postal_code}</p>
      </div>

      {order.status === 'paid' && (
        <button onClick={markAsShipped}>
          Mark as Shipped
        </button>
      )}

      {order.status === 'shipped' && (
        <div className="info">
          Waiting for buyer to confirm delivery...
        </div>
      )}

      {order.status === 'delivered' && (
        <div className="success">
          Order completed! Funds will be transferred to your account.
        </div>
      )}
    </div>
  );
}
```

### Buyer Order Tracking

```javascript
function BuyerOrderTracking({ orderId }) {
  const [order, setOrder] = useState(null);
  const token = localStorage.getItem('authToken');

  useEffect(() => {
    fetchOrder();
  }, [orderId]);

  const fetchOrder = async () => {
    const response = await axios.get(
      `http://localhost:8000/api/orders/${orderId}/`,
      {
        headers: { 'Authorization': `Token ${token}` }
      }
    );
    setOrder(response.data);
  };

  const markAsDelivered = async () => {
    if (!confirm('Have you received the item?')) return;

    try {
      await axios.post(
        `http://localhost:8000/api/orders/${orderId}/mark_delivered/`,
        {},
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      
      alert('Order marked as delivered!');
      fetchOrder();
      
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to mark as delivered');
    }
  };

  if (!order) return <div>Loading...</div>;

  return (
    <div className="order-tracking">
      <h2>Order #{order.order_number}</h2>
      
      {/* Order Timeline */}
      <div className="order-timeline">
        <div className={order.created_at ? 'completed' : ''}>
          <span>Order Placed</span>
          {order.created_at && (
            <small>{new Date(order.created_at).toLocaleString()}</small>
          )}
        </div>
        
        <div className={order.paid_at ? 'completed' : ''}>
          <span>Payment Confirmed</span>
          {order.paid_at && (
            <small>{new Date(order.paid_at).toLocaleString()}</small>
          )}
        </div>
        
        <div className={order.shipped_at ? 'completed' : ''}>
          <span>Shipped</span>
          {order.shipped_at && (
            <small>{new Date(order.shipped_at).toLocaleString()}</small>
          )}
        </div>
        
        <div className={order.delivered_at ? 'completed' : ''}>
          <span>Delivered</span>
          {order.delivered_at && (
            <small>{new Date(order.delivered_at).toLocaleString()}</small>
          )}
        </div>
      </div>

      {/* Order Details */}
      <div className="order-details">
        <p>Seller: {order.seller_username}</p>
        <p>Product: {order.product_name}</p>
        <p>Quantity: {order.quantity}</p>
        <p>Total Paid: PKR {order.total_amount}</p>
      </div>

      {/* Actions */}
      {order.status === 'pending_payment' && (
        <div>
          <p className="warning">Payment pending</p>
          <a href={order.payment_url} className="btn-primary">
            Complete Payment
          </a>
          <p>Deadline: {new Date(order.payment_deadline).toLocaleString()}</p>
        </div>
      )}

      {order.status === 'paid' && (
        <div className="info">
          Waiting for seller to ship the item...
        </div>
      )}

      {order.status === 'shipped' && (
        <div>
          <p className="success">Item has been shipped!</p>
          <button onClick={markAsDelivered}>
            Confirm Delivery
          </button>
        </div>
      )}

      {order.status === 'delivered' && (
        <div className="success">
          Order completed! Please leave feedback.
        </div>
      )}
    </div>
  );
}
```

---

## Error Handling

### Common Error Responses

**Order Not Found (404):**
```json
{
  "detail": "Not found."
}
```

**Unauthorized Access (403):**
```json
{
  "error": "You do not have permission to view this order"
}
```

**Invalid Status Transition (400):**
```json
{
  "error": "Order must be paid first"
}
```

---

**End of Orders & Payments API Documentation**
