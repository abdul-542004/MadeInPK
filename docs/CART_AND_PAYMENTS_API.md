# MadeInPK Shopping Cart & Payment API

**Base URL:** `http://localhost:8000/api/`

---

## Table of Contents

1. [Shopping Cart](#shopping-cart)
2. [Cart Operations](#cart-operations)
3. [Checkout Process](#checkout-process)
4. [Stripe Connect Integration](#stripe-connect-integration)
5. [Payment Processing](#payment-processing)

---

## Shopping Cart

The shopping cart allows buyers to add multiple fixed-price products from different sellers before checking out. Cart functionality is **only available for fixed-price listings**, not for auction items.

### Key Features

- Add multiple products from multiple sellers
- Update item quantities
- Remove items from cart
- Automatic price calculation with active discounts
- Single checkout for all items
- Automatic inventory validation

---

## Cart Operations

### Get User's Cart

**Endpoint:** `GET /api/cart/`

**Authentication:** Required

**Description:** Retrieve the current user's shopping cart with all items.

**Response (200 OK):**

```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "listing_id": 5,
      "product": {
        "id": 2,
        "seller": 5,
        "seller_username": "seller1",
        "category": 1,
        "category_name": "Textiles",
        "name": "Embroidered Cotton Kurti",
        "description": "Beautiful hand-embroidered cotton kurti...",
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
        "listing_type": "fixed_price"
      },
      "quantity": 2,
      "unit_price": "1200.00",
      "subtotal": "2400.00",
      "is_available": true,
      "seller_id": 5,
      "seller_username": "seller1",
      "added_at": "2025-11-10T10:00:00Z",
      "updated_at": "2025-11-10T10:00:00Z"
    },
    {
      "id": 2,
      "listing_id": 8,
      "product": {
        "id": 4,
        "seller": 6,
        "seller_username": "seller2",
        "category": 2,
        "category_name": "Handicrafts",
        "name": "Brass Wall Hanging",
        "description": "Intricately designed brass wall hanging...",
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
        "listing_type": "fixed_price"
      },
      "quantity": 1,
      "unit_price": "2560.00",
      "subtotal": "2560.00",
      "is_available": true,
      "seller_id": 6,
      "seller_username": "seller2",
      "added_at": "2025-11-10T11:00:00Z",
      "updated_at": "2025-11-10T11:00:00Z"
    }
  ],
  "total_items": 3,
  "total_price": "4960.00",
  "sellers": [
    {
      "id": 5,
      "username": "seller1"
    },
    {
      "id": 6,
      "username": "seller2"
    }
  ],
  "created_at": "2025-11-10T10:00:00Z",
  "updated_at": "2025-11-10T11:00:00Z"
}
```

### Add Item to Cart

**Endpoint:** `POST /api/cart/add_item/`

**Authentication:** Required

**Description:** Add a fixed-price listing to the cart. If the item already exists, the quantity is incremented.

**Request Body:**

```json
{
  "listing_id": 5,
  "quantity": 2
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| listing_id | integer | Yes | ID of the fixed-price listing |
| quantity | integer | Yes | Quantity to add (min 1) |

**Validation:**
- Listing must be active
- Cannot add own products to cart
- Must have sufficient stock available
- Only fixed-price listings can be added

**Response (201 Created):**

```json
{
  "id": 1,
  "listing_id": 5,
  "product": {
    "id": 2,
    "name": "Embroidered Cotton Kurti",
    "seller_username": "seller1"
  },
  "quantity": 2,
  "unit_price": "1200.00",
  "subtotal": "2400.00",
  "is_available": true,
  "seller_id": 5,
  "seller_username": "seller1",
  "added_at": "2025-11-10T10:00:00Z",
  "updated_at": "2025-11-10T10:00:00Z"
}
```

**Error Responses:**

```json
{
  "listing_id": ["Listing not found"]
}
```

```json
{
  "non_field_errors": ["This listing is not active"]
}
```

```json
{
  "non_field_errors": ["You cannot add your own products to cart"]
}
```

```json
{
  "quantity": ["Only 3 items available in stock"]
}
```

### Update Cart Item Quantity

**Endpoint:** `PATCH /api/cart/items/{item_id}/`

**Authentication:** Required

**Description:** Update the quantity of an item in the cart.

**Request Body:**

```json
{
  "quantity": 3
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "listing_id": 5,
  "product": {
    "id": 2,
    "name": "Embroidered Cotton Kurti"
  },
  "quantity": 3,
  "unit_price": "1200.00",
  "subtotal": "3600.00",
  "is_available": true,
  "seller_id": 5,
  "seller_username": "seller1",
  "added_at": "2025-11-10T10:00:00Z",
  "updated_at": "2025-11-10T12:00:00Z"
}
```

**Error (400 Bad Request):**

```json
{
  "quantity": ["Only 5 items available in stock"]
}
```

### Remove Item from Cart

**Endpoint:** `DELETE /api/cart/items/{item_id}/`

**Authentication:** Required

**Description:** Remove a specific item from the cart.

**Response (200 OK):**

```json
{
  "message": "Item removed from cart"
}
```

**Error (404 Not Found):**

```json
{
  "error": "Cart item not found"
}
```

### Clear Cart

**Endpoint:** `POST /api/cart/clear/`

**Authentication:** Required

**Description:** Remove all items from the cart.

**Response (200 OK):**

```json
{
  "message": "Cart cleared"
}
```

---

## Checkout Process

### Cart Checkout

**Endpoint:** `POST /api/cart/checkout/`

**Authentication:** Required

**Description:** Checkout the cart and create a multi-product order. This creates one order containing all cart items and initiates payment via Stripe.

**Request Body:**

```json
{
  "shipping_address_id": 1
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| shipping_address_id | integer | Yes | ID of shipping address |

**Validation:**
- Cart must not be empty
- All cart items must still be available
- Shipping address must belong to the user

**Response (201 Created):**

```json
{
  "id": 15,
  "order_number": "CART-A1B2C3D4E5F6",
  "buyer": 1,
  "buyer_username": "buyer1",
  "seller": null,
  "seller_username": null,
  "product": null,
  "product_name": null,
  "order_type": "cart",
  "quantity": null,
  "unit_price": null,
  "total_amount": "4960.00",
  "platform_fee": "99.20",
  "seller_amount": null,
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
  "status": "pending_payment",
  "payment_url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "payment_deadline": "2025-11-11T10:00:00Z",
  "items": [
    {
      "id": 1,
      "product": 2,
      "product_name": "Embroidered Cotton Kurti",
      "seller_id": 5,
      "seller_username": "seller1",
      "quantity": 2,
      "unit_price": "1200.00",
      "subtotal": "2400.00",
      "created_at": "2025-11-10T14:00:00Z"
    },
    {
      "id": 2,
      "product": 4,
      "product_name": "Brass Wall Hanging",
      "seller_id": 6,
      "seller_username": "seller2",
      "quantity": 1,
      "unit_price": "2560.00",
      "subtotal": "2560.00",
      "created_at": "2025-11-10T14:00:00Z"
    }
  ],
  "is_multi_seller": true,
  "stripe_payment_intent_id": "pi_...",
  "created_at": "2025-11-10T14:00:00Z",
  "paid_at": null,
  "shipped_at": null,
  "delivered_at": null
}
```

**Important Notes:**
- After successful checkout, the cart is automatically cleared
- Listing quantities are reduced immediately
- Payment must be completed within 24 hours
- The `payment_url` redirects to Stripe Checkout

**Error Responses:**

```json
{
  "non_field_errors": ["Cart is empty"]
}
```

```json
{
  "non_field_errors": ["The following items are no longer available: Embroidered Cotton Kurti"]
}
```

```json
{
  "shipping_address_id": ["Invalid shipping address"]
}
```

---

## Stripe Connect Integration

Sellers must connect their Stripe account to receive payments. The platform uses Stripe Connect Express for seller onboarding.

### Create Stripe Connect Account

**Endpoint:** `POST /api/stripe/connect/create_account/`

**Authentication:** Required (Seller role)

**Description:** Create a Stripe Connect Express account for the seller. Returns an onboarding URL to complete the setup.

**Requirements:**
- User must have seller role (`seller` or `both`)
- User must not already have a Stripe account

**Response (201 Created):**

```json
{
  "message": "Stripe Connect account created",
  "account_id": "acct_1234567890",
  "onboarding_url": "https://connect.stripe.com/setup/s/acct_1234567890/..."
}
```

**What to Do Next:**
Redirect the seller to the `onboarding_url` to complete their account setup with Stripe. They'll need to provide:
- Business information
- Bank account details
- Identity verification

**Error (403 Forbidden):**

```json
{
  "error": "Only sellers can create Stripe Connect accounts"
}
```

**Error (400 Bad Request):**

```json
{
  "error": "Stripe account already exists",
  "account_id": "acct_1234567890"
}
```

### Get Account Status

**Endpoint:** `GET /api/stripe/connect/account_status/`

**Authentication:** Required

**Description:** Check the status of the seller's Stripe Connect account.

**Response (200 OK):**

```json
{
  "charges_enabled": true,
  "payouts_enabled": true,
  "details_submitted": true,
  "requirements": {
    "currently_due": [],
    "eventually_due": [],
    "past_due": [],
    "pending_verification": []
  }
}
```

**Status Fields:**
- `charges_enabled`: Can accept payments
- `payouts_enabled`: Can receive payouts
- `details_submitted`: Has completed onboarding
- `requirements`: Any missing information

**Error (404 Not Found):**

```json
{
  "error": "No Stripe account found"
}
```

### Refresh Onboarding Link

**Endpoint:** `POST /api/stripe/connect/refresh_onboarding/`

**Authentication:** Required

**Description:** Generate a new onboarding link if the seller needs to update their information or if the previous link expired.

**Response (200 OK):**

```json
{
  "onboarding_url": "https://connect.stripe.com/setup/s/acct_1234567890/..."
}
```

### Onboarding Return/Refresh Pages

**Return Page:** `GET /api/stripe/connect/return_page/`
- Accessed after successful onboarding completion

**Refresh Page:** `GET /api/stripe/connect/refresh_page/`
- Accessed if seller needs to complete additional information

---

## Payment Processing

### Payment Flow Overview

```
1. Buyer checks out cart
   ↓
2. Order created with status: pending_payment
   ↓
3. Buyer redirected to Stripe Checkout
   ↓
4. Buyer completes payment
   ↓
5. Stripe webhook notifies backend
   ↓
6. Order status updated to: paid
   ↓
7. For cart orders: Funds distributed to sellers
   ↓
8. Sellers ship items
   ↓
9. Buyer confirms delivery
```

### Multi-Seller Payment Distribution

For cart orders with multiple sellers:

1. **Platform receives full payment** from buyer
2. **Platform fee (2%) calculated** for total order
3. **Funds distributed to each seller** based on their items:
   - Per seller: `(Seller's items subtotal - 2% fee)`
   - Transfers happen automatically after payment success

**Example:**

```
Total Order: PKR 4,960
Platform Fee (2%): PKR 99.20

Seller 1 Items: PKR 2,400
Seller 1 Receives: PKR 2,352 (PKR 2,400 - 2%)

Seller 2 Items: PKR 2,560  
Seller 2 Receives: PKR 2,508.80 (PKR 2,560 - 2%)
```

### Payment Success Page

**Endpoint:** `GET /api/payments/success/?order_id={id}`

**Authentication:** Required

**Description:** Redirect page after successful payment.

**Response (200 OK):**

```json
{
  "message": "Payment successful",
  "order": {
    "id": 15,
    "order_number": "CART-A1B2C3D4E5F6",
    "status": "paid",
    "total_amount": "4960.00"
  }
}
```

### Payment Cancel Page

**Endpoint:** `GET /api/payments/cancel/?order_id={id}`

**Authentication:** Required

**Description:** Redirect page if payment is cancelled.

**Response (200 OK):**

```json
{
  "message": "Payment cancelled",
  "order": {
    "id": 15,
    "order_number": "CART-A1B2C3D4E5F6",
    "status": "pending_payment"
  },
  "payment_url": "https://checkout.stripe.com/c/pay/cs_test_..."
}
```

### Stripe Webhook

**Endpoint:** `POST /api/stripe/webhook/`

**Authentication:** Not required (uses Stripe signature)

**Description:** Receives payment events from Stripe. This endpoint is called by Stripe, not by your frontend.

**Webhook Configuration:**
Add this endpoint to your Stripe Dashboard webhook settings:
```
https://yourdomain.com/api/stripe/webhook/
```

**Events Handled:**
- `payment_intent.succeeded` - Payment successful
- `payment_intent.payment_failed` - Payment failed
- `account.updated` - Seller account updated

**Response:**

```json
{
  "status": "success"
}
```

---

## Complete Frontend Examples

### Cart Management Component

```javascript
import { useState, useEffect } from 'react';
import axios from 'axios';

function ShoppingCart() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('authToken');

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await axios.get(
        'http://localhost:8000/api/cart/',
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      setCart(response.data);
    } catch (error) {
      console.error('Failed to fetch cart:', error);
    }
  };

  const addToCart = async (listingId, quantity) => {
    setLoading(true);
    try {
      await axios.post(
        'http://localhost:8000/api/cart/add_item/',
        {
          listing_id: listingId,
          quantity: quantity
        },
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      fetchCart(); // Refresh cart
      alert('Item added to cart!');
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to add item');
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId, newQuantity) => {
    try {
      await axios.patch(
        `http://localhost:8000/api/cart/items/${itemId}/`,
        { quantity: newQuantity },
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      fetchCart();
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to update quantity');
    }
  };

  const removeItem = async (itemId) => {
    if (!confirm('Remove this item from cart?')) return;

    try {
      await axios.delete(
        `http://localhost:8000/api/cart/items/${itemId}/`,
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      fetchCart();
    } catch (error) {
      alert('Failed to remove item');
    }
  };

  const checkout = async (addressId) => {
    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:8000/api/cart/checkout/',
        { shipping_address_id: addressId },
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );

      // Redirect to Stripe Checkout
      window.location.href = response.data.payment_url;
    } catch (error) {
      alert(error.response?.data?.error || 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  if (!cart) return <div>Loading...</div>;

  return (
    <div className="shopping-cart">
      <h2>Shopping Cart ({cart.total_items} items)</h2>

      {cart.items.length === 0 ? (
        <p>Your cart is empty</p>
      ) : (
        <>
          {cart.items.map(item => (
            <div key={item.id} className="cart-item">
              <img src={item.product.images[0]?.image_url} alt={item.product.name} />
              <div>
                <h3>{item.product.name}</h3>
                <p>Seller: {item.seller_username}</p>
                <p>Price: PKR {item.unit_price}</p>
                
                <div className="quantity-controls">
                  <button onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          disabled={item.quantity <= 1}>
                    -
                  </button>
                  <span>{item.quantity}</span>
                  <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>
                    +
                  </button>
                </div>

                <p>Subtotal: PKR {item.subtotal}</p>
                {!item.is_available && (
                  <p className="error">Item no longer available</p>
                )}
              </div>

              <button onClick={() => removeItem(item.id)}>Remove</button>
            </div>
          ))}

          <div className="cart-summary">
            <h3>Order Summary</h3>
            <p>Subtotal: PKR {cart.total_price}</p>
            <p>Platform Fee (2%): PKR {(parseFloat(cart.total_price) * 0.02).toFixed(2)}</p>
            <p><strong>Total: PKR {cart.total_price}</strong></p>

            <button 
              onClick={() => checkout(selectedAddressId)} 
              disabled={loading || cart.items.length === 0}
            >
              {loading ? 'Processing...' : 'Proceed to Checkout'}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
```

### Seller Stripe Connect Setup

```javascript
function SellerStripeSetup() {
  const [accountStatus, setAccountStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('authToken');

  useEffect(() => {
    checkAccountStatus();
  }, []);

  const checkAccountStatus = async () => {
    try {
      const response = await axios.get(
        'http://localhost:8000/api/stripe/connect/account_status/',
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      setAccountStatus(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        setAccountStatus(null); // No account yet
      }
    }
  };

  const createAccount = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:8000/api/stripe/connect/create_account/',
        {},
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );

      // Redirect to Stripe onboarding
      window.location.href = response.data.onboarding_url;
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  const refreshOnboarding = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:8000/api/stripe/connect/refresh_onboarding/',
        {},
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );

      window.location.href = response.data.onboarding_url;
    } catch (error) {
      alert('Failed to refresh onboarding');
    } finally {
      setLoading(false);
    }
  };

  if (accountStatus === null) {
    return (
      <div className="stripe-setup">
        <h2>Connect Your Stripe Account</h2>
        <p>To receive payments, you need to connect a Stripe account.</p>
        <button onClick={createAccount} disabled={loading}>
          {loading ? 'Creating...' : 'Connect Stripe Account'}
        </button>
      </div>
    );
  }

  return (
    <div className="stripe-status">
      <h2>Stripe Account Status</h2>
      <p>Charges Enabled: {accountStatus.charges_enabled ? '✓' : '✗'}</p>
      <p>Payouts Enabled: {accountStatus.payouts_enabled ? '✓' : '✗'}</p>
      <p>Details Submitted: {accountStatus.details_submitted ? '✓' : '✗'}</p>

      {!accountStatus.details_submitted && (
        <div>
          <p className="warning">Please complete your account setup</p>
          <button onClick={refreshOnboarding}>
            Complete Setup
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## Important Notes

### Cart Limitations

1. **Fixed-Price Only**: Only fixed-price listings can be added to cart
2. **Auction Items**: Must be purchased individually after winning
3. **Own Products**: Sellers cannot add their own products to cart
4. **Stock Validation**: Cart validates stock availability at checkout

### Payment Timeline

- **Payment Deadline**: 24 hours from order creation
- **Failed Payment Consequences**:
  - User's `failed_payment_count` increments
  - After 3 failed payments, account is blocked
  - For auctions: Payment violation recorded

### Platform Fees

- **Standard Fee**: 2% on all transactions
- **Calculation**: Applied to each seller's subtotal in multi-seller orders
- **Deduction**: Automatic from transfers to sellers

### Seller Requirements

- Must have `seller` or `both` role
- Must complete Stripe Connect onboarding
- Bank account must be verified
- Identity verification may be required

---

**End of Shopping Cart & Payment API Documentation**
