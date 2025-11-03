# MadeInPK WebSocket Documentation

**Base WebSocket URL:** `ws://localhost:8000/ws/`

> **📝 Last Updated:** November 4, 2025  
> **✨ Recent Changes:** 
> - Added automatic email and in-app notification when users are outbid
> - Enhanced initial connection response to include comprehensive product details, seller information with ratings, product images, start time, and total bid count

---

## Overview

MadeInPK uses Django Channels for real-time bidding functionality. WebSocket connections enable live auction updates without polling, providing instant notifications when bids are placed.

Upon connection, the server immediately sends complete auction data including:
- **Product details** (name, description, condition, category, images)
- **Seller information** (brand name, biography, verification status, ratings)
- **Auction details** (starting price, current price, start/end times, bid history)
- **Real-time updates** (new bids, auction status changes)

---

## Auction WebSocket

### Connection Endpoint

```
ws://localhost:8000/ws/auction/{auction_id}/
```

**Authentication:** Token-based (pass token in query parameter)

### Example Connection URLs

```
ws://localhost:8000/ws/auction/1/?token=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
ws://localhost:8000/ws/auction/2/?token=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

---

## JavaScript/React Connection Setup

### Basic WebSocket Connection

```javascript
const auctionId = 1;
const token = localStorage.getItem('authToken');

// Create WebSocket connection
const socket = new WebSocket(
  `ws://localhost:8000/ws/auction/${auctionId}/?token=${token}`
);

// Connection opened
socket.onopen = (event) => {
  console.log('Connected to auction:', auctionId);
};

// Listen for messages
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  handleAuctionUpdate(data);
};

// Handle errors
socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Connection closed
socket.onclose = (event) => {
  console.log('Disconnected from auction');
  if (event.wasClean) {
    console.log(`Closed cleanly, code=${event.code}, reason=${event.reason}`);
  } else {
    console.log('Connection died');
  }
};
```

---

## Message Types

### 1. Initial Connection Response (Server → Client)

When you successfully connect to an auction, the server immediately sends comprehensive auction data including product details, seller information, and images.

**Message Type:** `auction_status`

**Example Response:**

```json
{
  "type": "auction_status",
  "data": {
    "auction_id": 1,
    "product": {
      "id": 1,
      "name": "Handwoven Pashmina Shawl",
      "description": "Luxurious handwoven Pashmina shawl made from the finest Kashmiri wool. Features intricate embroidery and traditional patterns. Perfect for special occasions or as a statement piece.",
      "condition": "new",
      "category": "Textiles & Fabrics",
      "images": [
        {
          "url": "/media/products/shawl_primary.jpg",
          "is_primary": true,
          "order": 0
        },
        {
          "url": "/media/products/shawl_detail1.jpg",
          "is_primary": false,
          "order": 1
        },
        {
          "url": "/media/products/shawl_detail2.jpg",
          "is_primary": false,
          "order": 2
        }
      ]
    },
    "seller": {
      "id": 5,
      "username": "kashmiri_crafts",
      "email": "seller@example.com",
      "brand_name": "Kashmiri Heritage Crafts",
      "biography": "We specialize in authentic Kashmiri handicrafts, bringing you the finest traditional products directly from local artisans.",
      "is_verified": true,
      "average_rating": "4.85",
      "total_feedbacks": 127
    },
    "starting_price": "2500.00",
    "current_price": "2875.00",
    "start_time": "2025-10-27T10:00:00Z",
    "end_time": "2025-10-29T23:27:00Z",
    "status": "active",
    "is_active": true,
    "winner": null,
    "total_bids": 12,
    "latest_bids": [
      {
        "bidder": "buyer2",
        "amount": "2875.00",
        "time": "2025-10-27T18:32:00Z"
      },
      {
        "bidder": "buyer1",
        "amount": "2750.00",
        "time": "2025-10-27T18:15:00Z"
      },
      {
        "bidder": "buyer3",
        "amount": "2625.00",
        "time": "2025-10-27T18:00:00Z"
      },
      {
        "bidder": "buyer2",
        "amount": "2500.00",
        "time": "2025-10-27T17:45:00Z"
      }
    ]
  }
}
```

**Fields:**

#### Product Object
- `id` - Product identifier
- `name` - Product name
- `description` - Full product description
- `condition` - Product condition (new, like_new, good, fair)
- `category` - Product category name
- `images` - Array of product images
  - `url` - Image URL (relative path from media root)
  - `is_primary` - Boolean indicating if this is the primary image
  - `order` - Display order for images

#### Seller Object
- `id` - Seller user ID
- `username` - Seller username
- `email` - Seller email address
- `brand_name` - Seller's brand/business name (if available)
- `biography` - Seller's business description (if available)
- `is_verified` - Boolean indicating if seller is verified by admin
- `average_rating` - Seller's average rating (0.00 to 5.00)
- `total_feedbacks` - Total number of feedbacks received

#### Auction Details
- `auction_id` - Auction identifier
- `starting_price` - Initial auction starting price
- `current_price` - Current highest bid amount
- `start_time` - ISO 8601 timestamp when auction started
- `end_time` - ISO 8601 timestamp when auction ends
- `status` - Auction status (active, ended, cancelled, completed)
- `is_active` - Boolean indicating if auction is currently active
- `winner` - Winner object (null if no winner yet)
  - `id` - Winner user ID
  - `username` - Winner username
- `total_bids` - Total number of bids placed
- `latest_bids` - Array of last 5 bids (most recent first)

---

### 2. Place a Bid (Client → Server)

Send this message to place a bid on the auction.

**Message Type:** `place_bid`

**Request Format:**

```json
{
  "type": "place_bid",
  "amount": 3000.00
}
```

**JavaScript Example:**

```javascript
function placeBid(amount) {
  const bidData = {
    type: 'place_bid',
    amount: parseFloat(amount)
  };
  
  socket.send(JSON.stringify(bidData));
}

// Usage
placeBid(3000.00);
```

**Validation Rules:**
- Amount must be higher than current price
- User must be authenticated
- User cannot bid on their own auction
- User account must not be blocked
- Auction must be active

---

### 3. New Bid Notification (Server → All Clients)

When any user successfully places a bid, ALL connected clients watching this auction receive this notification.

**Message Type:** `new_bid`

**Example Response:**

```json
{
  "type": "new_bid",
  "data": {
    "bidder": "buyer1",
    "amount": "3000.00",
    "time": "2025-10-27T18:45:00Z",
    "current_price": "3000.00"
  }
}
```

**Fields:**
- `bidder` - Username of the bidder
- `amount` - Bid amount
- `time` - ISO 8601 timestamp when bid was placed
- `current_price` - Updated current price (same as amount)

**Use Case:** Update UI to show new highest bid and notify users they've been outbid.

**📧 Automatic Notifications:**

When a user is outbid, they automatically receive:

1. **In-app notification** - Stored in the database and viewable in their notifications panel
2. **Email notification** - Sent asynchronously via Celery task

**Email Example:**
```
Subject: You have been outbid on Handwoven Pashmina Shawl

Dear buyer1,

You have been outbid on the auction for Handwoven Pashmina Shawl.

New highest bid: Rs. 3000.00

If you're still interested, you can place a higher bid to regain the lead.

Log in to your MadeInPK account to view the auction and place a new bid.

Thank you for using MadeInPK!
```

**In-app Notification:**
```json
{
  "notification_type": "bid_outbid",
  "title": "You have been outbid",
  "message": "Someone placed a higher bid of Rs. 3000.00 on Handwoven Pashmina Shawl",
  "auction": 1,
  "is_read": false,
  "created_at": "2025-11-04T18:45:00Z"
}
```

---

### 4. Error Response (Server → Client)

If a bid fails validation, only the user who attempted the bid receives an error message.

**Message Type:** `error`

**Example Response:**

```json
{
  "type": "error",
  "message": "Bid must be higher than current price of 2875.00"
}
```

**Possible Error Messages:**

| Error Message | Cause |
|---------------|-------|
| `"Auction is not active"` | Auction has ended or hasn't started |
| `"Your account is blocked"` | User account is blocked due to payment violations |
| `"Bid must be higher than current price of X"` | Bid amount is too low |
| `"You cannot bid on your own auction"` | Seller trying to bid on their own item |
| `"Auction not found"` | Invalid auction ID |

**Note:** When placing a bid that's higher than the current price, the previous highest bidder will automatically receive both an email and in-app notification informing them they've been outbid.

---

### 5. Auction Ended (Server → All Clients)

When an auction ends (either by time expiration or manual closure), all connected clients receive this notification.

**Message Type:** `auction_ended`

**Example Response:**

```json
{
  "type": "auction_ended",
  "data": {
    "auction_id": 1,
    "winner": "buyer1",
    "final_price": "3000.00",
    "status": "ended"
  }
}
```

**Fields:**
- `auction_id` - Auction identifier
- `winner` - Username of the winning bidder
- `final_price` - Final winning bid amount
- `status` - New auction status (ended)

---

## Complete React Hook Example

Here's a production-ready React hook for managing auction WebSocket connections:

```javascript
import { useEffect, useState, useRef, useCallback } from 'react';

/**
 * Custom hook for managing auction WebSocket connection
 * @param {number} auctionId - The auction ID to connect to
 * @param {string} token - Authentication token
 * @returns {object} - { auctionData, isConnected, placeBid, error }
 */
function useAuctionWebSocket(auctionId, token) {
  const [auctionData, setAuctionData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Place bid function
  const placeBid = useCallback((amount) => {
    if (socketRef.current && isConnected) {
      const bidData = {
        type: 'place_bid',
        amount: parseFloat(amount)
      };
      socketRef.current.send(JSON.stringify(bidData));
      return true;
    }
    console.error('Cannot place bid: WebSocket not connected');
    return false;
  }, [isConnected]);

  useEffect(() => {
    if (!auctionId || !token) return;

    // Create WebSocket connection
    const wsUrl = `ws://localhost:8000/ws/auction/${auctionId}/?token=${token}`;
    socketRef.current = new WebSocket(wsUrl);

    socketRef.current.onopen = () => {
      console.log('WebSocket Connected to auction:', auctionId);
      setIsConnected(true);
      setError(null);
    };

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch(data.type) {
        case 'auction_status':
          // Initial auction data
          setAuctionData(data.data);
          break;
          
        case 'new_bid':
          // Update auction with new bid
          setAuctionData(prev => {
            if (!prev) return prev;
            
            return {
              ...prev,
              current_price: data.data.current_price,
              total_bids: (prev.total_bids || 0) + 1,
              latest_bids: [
                data.data,
                ...prev.latest_bids.slice(0, 4) // Keep only 5 most recent
              ]
            };
          });
          
          // Note: If you were the previous highest bidder and got outbid,
          // you'll receive an email and in-app notification automatically
          break;
          
        case 'auction_ended':
          // Auction has ended
          setAuctionData(prev => ({
            ...prev,
            status: 'ended',
            winner: data.data.winner,
            final_price: data.data.final_price
          }));
          break;
          
        case 'error':
          // Error from server
          setError(data.message);
          // Clear error after 5 seconds
          setTimeout(() => setError(null), 5000);
          break;
          
        default:
          console.warn('Unknown message type:', data.type);
      }
    };

    socketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error occurred');
    };

    socketRef.current.onclose = (event) => {
      console.log('WebSocket Disconnected');
      setIsConnected(false);
      
      // Attempt to reconnect after 3 seconds
      if (!event.wasClean) {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          // Trigger re-render to reconnect
          setAuctionData(prev => ({ ...prev }));
        }, 3000);
      }
    };

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [auctionId, token]);

  return { 
    auctionData, 
    isConnected, 
    placeBid, 
    error 
  };
}

export default useAuctionWebSocket;
```

---

## Usage in React Component

```javascript
import React, { useState } from 'react';
import useAuctionWebSocket from './hooks/useAuctionWebSocket';

function AuctionPage({ auctionId }) {
  const token = localStorage.getItem('authToken');
  const { auctionData, isConnected, placeBid, error } = useAuctionWebSocket(auctionId, token);
  const [bidAmount, setBidAmount] = useState('');

  const handleBidSubmit = (e) => {
    e.preventDefault();
    
    if (!bidAmount || parseFloat(bidAmount) <= 0) {
      alert('Please enter a valid bid amount');
      return;
    }

    const success = placeBid(bidAmount);
    if (success) {
      setBidAmount(''); // Clear input
    }
  };

  if (!auctionData) {
    return <div>Loading auction data...</div>;
  }

  const timeRemaining = new Date(auctionData.end_time) - new Date();
  const isActive = auctionData.status === 'active' && timeRemaining > 0;

  return (
    <div className="auction-page">
      {/* Connection Status */}
      <div className="connection-status">
        {isConnected ? (
          <span className="status-connected">🟢 Live</span>
        ) : (
          <span className="status-disconnected">🔴 Disconnected</span>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Product Images */}
      <div className="product-images">
        {auctionData.product.images && auctionData.product.images.length > 0 ? (
          <img 
            src={auctionData.product.images.find(img => img.is_primary)?.url || auctionData.product.images[0].url}
            alt={auctionData.product.name}
            className="primary-image"
          />
        ) : (
          <div className="no-image">No image available</div>
        )}
      </div>

      {/* Auction Info */}
      <h1>{auctionData.product.name}</h1>
      <p className="product-description">{auctionData.product.description}</p>
      <p className="product-condition">
        Condition: <strong>{auctionData.product.condition}</strong>
      </p>
      
      {/* Seller Info */}
      <div className="seller-info">
        <h3>Seller: {auctionData.seller.brand_name || auctionData.seller.username}</h3>
        {auctionData.seller.is_verified && <span className="verified-badge">✓ Verified</span>}
        <p>Rating: {auctionData.seller.average_rating} ⭐ ({auctionData.seller.total_feedbacks} reviews)</p>
        {auctionData.seller.biography && <p className="seller-bio">{auctionData.seller.biography}</p>}
      </div>

      <div className="auction-info">
        <p className="starting-price">
          Starting Price: <strong>PKR {auctionData.starting_price}</strong>
        </p>
        <p className="current-price">
          Current Price: <strong>PKR {auctionData.current_price}</strong>
        </p>
        <p className="status">
          Status: <span className={`status-${auctionData.status}`}>
            {auctionData.status.toUpperCase()}
          </span>
        </p>
        <p className="start-time">
          Started: {new Date(auctionData.start_time).toLocaleString()}
        </p>
        <p className="end-time">
          Ends: {new Date(auctionData.end_time).toLocaleString()}
        </p>
        <p className="total-bids">
          Total Bids: <strong>{auctionData.total_bids}</strong>
        </p>
      </div>

      {/* Bid Form */}
      {isActive && (
        <form onSubmit={handleBidSubmit} className="bid-form">
          <input
            type="number"
            step="0.01"
            min={parseFloat(auctionData.current_price) + 0.01}
            value={bidAmount}
            onChange={(e) => setBidAmount(e.target.value)}
            placeholder={`Min: ${parseFloat(auctionData.current_price) + 1}`}
            required
          />
          <button type="submit" disabled={!isConnected}>
            Place Bid
          </button>
        </form>
      )}

      {/* Bid History */}
      <div className="bid-history">
        <h3>Recent Bids</h3>
        {auctionData.latest_bids && auctionData.latest_bids.length > 0 ? (
          <ul>
            {auctionData.latest_bids.map((bid, index) => (
              <li key={index} className={index === 0 ? 'winning-bid' : ''}>
                <span className="bidder">{bid.bidder}</span>
                <span className="amount">PKR {bid.amount}</span>
                <span className="time">
                  {new Date(bid.time).toLocaleTimeString()}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p>No bids yet. Be the first to bid!</p>
        )}
      </div>

      {/* Auction Ended */}
      {auctionData.status === 'ended' && auctionData.winner && (
        <div className="auction-ended">
          <h2>Auction Ended</h2>
          <p>Winner: <strong>{auctionData.winner}</strong></p>
          <p>Final Price: <strong>PKR {auctionData.final_price || auctionData.current_price}</strong></p>
        </div>
      )}
    </div>
  );
}

export default AuctionPage;
```

---

## Testing WebSocket Connection

### Using Browser Console

```javascript
// Open browser console and run:
const ws = new WebSocket('ws://localhost:8000/ws/auction/1/?token=YOUR_TOKEN');

ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));

// Place a test bid
ws.send(JSON.stringify({ type: 'place_bid', amount: 3000 }));
```

### Using wscat (CLI tool)

```bash
# Install wscat
npm install -g wscat

# Connect to auction
wscat -c "ws://localhost:8000/ws/auction/1/?token=YOUR_TOKEN"

# Send bid
> {"type": "place_bid", "amount": 3000}
```

---

## Notification System

### Outbid Notifications

When a user places a higher bid than you, the system automatically:

1. **Creates an in-app notification** with type `bid_outbid`
2. **Sends an email** to the outbid user
3. **Updates the bid status** in the database

**Notification Flow:**

```
User A has winning bid of Rs. 2,875
           ↓
User B places bid of Rs. 3,000
           ↓
System processes:
  - Mark User A's bid as not winning
  - Create User B's bid as winning
  - Create notification for User A
  - Send email to User A (async via Celery)
           ↓
User A receives:
  - Real-time WebSocket update (if connected)
  - In-app notification badge
  - Email notification
```

### Accessing Notifications via API

Users can retrieve their notifications using the REST API:

```http
GET /api/notifications/
Authorization: Token YOUR_AUTH_TOKEN
```

**Response:**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 42,
      "notification_type": "bid_outbid",
      "title": "You have been outbid",
      "message": "Someone placed a higher bid of Rs. 3000.00 on Handwoven Pashmina Shawl",
      "is_read": false,
      "auction": {
        "id": 1,
        "product_name": "Handwoven Pashmina Shawl",
        "current_price": "3000.00"
      },
      "created_at": "2025-11-04T18:45:00Z"
    }
  ]
}
```

---

## Best Practices

### 1. Handle Reconnection

Always implement reconnection logic for dropped connections:

```javascript
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connectWebSocket() {
  const socket = new WebSocket(wsUrl);
  
  socket.onclose = () => {
    if (reconnectAttempts < maxReconnectAttempts) {
      reconnectAttempts++;
      setTimeout(connectWebSocket, 3000 * reconnectAttempts);
    }
  };
  
  socket.onopen = () => {
    reconnectAttempts = 0; // Reset on successful connection
  };
}
```

### 2. Validate Before Sending

```javascript
function placeBid(amount) {
  // Client-side validation
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.error('WebSocket not connected');
    return false;
  }
  
  if (amount <= currentPrice) {
    console.error('Bid must be higher than current price');
    return false;
  }
  
  socket.send(JSON.stringify({ type: 'place_bid', amount }));
  return true;
}
```

### 3. Clean Up Resources

```javascript
useEffect(() => {
  const socket = new WebSocket(wsUrl);
  
  return () => {
    // Always close socket on unmount
    if (socket.readyState === WebSocket.OPEN) {
      socket.close();
    }
  };
}, []);
```

### 4. Handle Multiple Tabs

If user opens multiple tabs, each will have its own WebSocket connection. Consider using BroadcastChannel API to sync state across tabs.

---

## Troubleshooting

### Connection Refused

**Error:** `WebSocket connection failed`

**Solutions:**
- Ensure Django server is running
- Check if Redis is running (required for Channels)
- Verify ASGI configuration in settings.py

### Authentication Failed

**Error:** Connection closes immediately after opening

**Solutions:**
- Verify token is valid and not expired
- Check token format in URL: `?token=YOUR_TOKEN`
- Ensure user is authenticated

### Messages Not Received

**Solutions:**
- Check browser console for errors
- Verify JSON.parse() is used on received messages
- Ensure onmessage handler is properly set

---

## Sample Auction IDs (from populate_db)

| Auction ID | Product Name | Starting Price |
|------------|--------------|----------------|
| 1 | Handwoven Pashmina Shawl | PKR 2,500 |
| 2 | Silk Bedspread Set | PKR 8,500 |
| 3 | Wooden Jewelry Box | PKR 1,800 |
| 4 | Ceramic Dinner Set | PKR 4,200 |
| 5 | Gold-Plated Earrings Set | PKR 1,200 |
| 6 | Kashmiri Silk Carpet | PKR 25,000 |

---

**End of WebSocket Documentation**
