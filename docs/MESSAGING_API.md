# MadeInPK Messaging API Documentation

**Base URL:** `http://localhost:8000/api/`

---

## Table of Contents

1. [Overview](#overview)
2. [Data Models](#data-models)
3. [Understanding the Product Field](#understanding-the-product-field)
4. [Endpoints](#endpoints)
5. [Business Logic](#business-logic)
6. [Common Use Cases](#common-use-cases)
7. [Error Responses](#error-responses)
8. [Usage Examples](#usage-examples)
9. [WebSocket Integration](#websocket-integration)

---

## Overview

The Messaging API enables real-time communication between buyers and sellers on the MadeInPK platform. Conversations are typically linked to specific products, allowing buyers to inquire about items they're interested in before or after making a purchase.

### Key Features

- **Product-Specific Conversations**: Link conversations to products for contextual communication
- **Pre-Purchase Inquiries**: Ask questions before buying
- **Post-Purchase Support**: Discuss shipping, quality, or issues after purchase
- **Read Status Tracking**: Know when messages have been read
- **Unread Message Count**: See how many unread messages you have per conversation
- **Automatic Notifications**: Recipients get notified of new messages

---

## Data Models

### Conversation

```json
{
  "id": 1,
  "buyer": 123,
  "buyer_username": "buyer_user",
  "seller": 456,
  "seller_username": "seller_user",
  "product": 789,
  "product_name": "Handwoven Pashmina Shawl",
  "product_image": "http://localhost:8000/media/products/pashmina.jpg",
  "latest_message": {
    "id": 5,
    "sender": 123,
    "sender_username": "buyer_user",
    "content": "Is this still available?",
    "is_read": false,
    "created_at": "2025-11-12T10:30:00Z"
  },
  "unread_count": 2,
  "created_at": "2025-11-12T10:00:00Z",
  "updated_at": "2025-11-12T10:30:00Z"
}
```

### Message

```json
{
  "id": 1,
  "sender": 123,
  "sender_username": "buyer_user",
  "content": "Hello, is this item still available?",
  "is_read": false,
  "created_at": "2025-11-12T10:30:00Z"
}
```

---

## Understanding the Product Field

### Purpose of the Product Field

The `product` foreign key in the `Conversation` model serves as the central context for buyer-seller communication. This design enables several important features:

#### 1. **Pre-Purchase Inquiries**
Buyers can ask questions about products before making a purchase:
- **Product Questions**: "What size is this?" or "Is this available in blue?"
- **Availability**: "When will this be back in stock?"
- **Condition Details**: "Can you send more photos?"
- **Shipping Information**: "Do you ship to my city?"
- **Negotiation**: "Can you offer a discount for bulk orders?"

#### 2. **Contextual Communication**
Product information provides immediate context for the conversation:
- **Visual Context**: Product image displayed in conversation list
- **Product Details**: Name, price, and seller information readily available
- **Listing Type**: Know if it's an auction or fixed-price item
- **Stock Status**: See if the item is still available

#### 3. **Post-Purchase Support**
After buying, the same conversation continues with product context:
- **Usage Questions**: "How do I care for this fabric?"
- **Quality Concerns**: "The color seems different from the photo"
- **Shipping Updates**: "Has this been shipped yet?"
- **Follow-up Orders**: "Do you have more of these?"

#### 4. **Optional Field Flexibility**
The field is marked as `null=True, blank=True`, which means:
- **General Inquiries**: Conversations can exist without a product for general seller questions
- **Shop Policies**: Ask about return policies, payment methods, or business hours
- **Custom Orders**: Discuss custom products not yet listed
- **Business Inquiries**: Wholesale or partnership discussions

### Database Relationship

```python
# In the Conversation model
product = models.ForeignKey(
    Product, 
    on_delete=models.CASCADE, 
    related_name='conversations', 
    null=True,      # Database allows NULL values
    blank=True      # Django forms/serializers allow empty values
)
```

**Relationship Type**: Many-to-One (Multiple conversations can reference the same product)

**Cascade Behavior**: `on_delete=models.CASCADE` - If a product is deleted, all related conversations are also deleted

**Unique Constraint**: Combined with `unique_together = ['buyer', 'seller', 'product']` - Ensures only one conversation per buyer-seller-product combination

### Use Cases

#### Scenario 1: Pre-Purchase Product Inquiry
```json
{
  "buyer": 123,
  "seller": 456,
  "product": 789,
  "latest_message": {
    "content": "Hi! What material is this shawl made of?"
  }
}
```

#### Scenario 2: General Seller Inquiry
```json
{
  "buyer": 123,
  "seller": 456,
  "product": null,
  "latest_message": {
    "content": "Do you accept custom orders?"
  }
}
```

#### Scenario 3: Multiple Products, Different Conversations
```json
[
  {
    "id": 1,
    "buyer": 123,
    "seller": 456,
    "product": 789,
    "product_name": "Pashmina Shawl",
    "latest_message": { "content": "Is the blue one available?" }
  },
  {
    "id": 2,
    "buyer": 123,
    "seller": 456,
    "product": 790,
    "product_name": "Embroidered Kurti",
    "latest_message": { "content": "What sizes do you have?" }
  }
]
```

---

## Endpoints

### 1. List Conversations

**Endpoint:** `GET /api/conversations/`

**Authentication:** Required

**Description:** Retrieves all conversations for the authenticated user (as buyer or seller).

**Response (200 OK):**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "buyer": 123,
      "buyer_username": "buyer_user",
      "seller": 456,
      "seller_username": "seller_user",
      "product": 789,
      "product_name": "Handwoven Pashmina Shawl",
      "product_image": "http://localhost:8000/media/products/pashmina.jpg",
      "latest_message": {
        "id": 5,
        "sender": 456,
        "sender_username": "seller_user",
        "content": "Yes, it's available in blue!",
        "is_read": false,
        "created_at": "2025-11-12T10:45:00Z"
      },
      "unread_count": 2,
      "created_at": "2025-11-12T10:00:00Z",
      "updated_at": "2025-11-12T10:45:00Z"
    },
    {
      "id": 2,
      "buyer": 123,
      "buyer_username": "buyer_user",
      "seller": 789,
      "seller_username": "another_seller",
      "product": null,
      "product_name": null,
      "product_image": null,
      "latest_message": {
        "id": 8,
        "sender": 789,
        "sender_username": "another_seller",
        "content": "Yes, I do custom orders. What are you looking for?",
        "is_read": false,
        "created_at": "2025-11-12T09:30:00Z"
      },
      "unread_count": 1,
      "created_at": "2025-11-12T09:00:00Z",
      "updated_at": "2025-11-12T09:30:00Z"
    }
  ]
}
```

**Notes:**
- Conversations without products (general inquiries) will have `product: null`, `product_name: null`, and `product_image: null`
- Ordered by most recent update first

---

### 2. Create Conversation

**Endpoint:** `POST /api/conversations/`

**Authentication:** Required

**Description:** Creates a new conversation. The `product` field is optional.

#### With a Product (Product Inquiry)

**Request Body:**

```json
{
  "buyer": 123,
  "seller": 456,
  "product": 789
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "buyer": 123,
  "buyer_username": "buyer_user",
  "seller": 456,
  "seller_username": "seller_user",
  "product": 789,
  "product_name": "Handwoven Pashmina Shawl",
  "product_image": "http://localhost:8000/media/products/pashmina.jpg",
  "latest_message": null,
  "unread_count": 0,
  "created_at": "2025-11-12T10:00:00Z",
  "updated_at": "2025-11-12T10:00:00Z"
}
```

#### Without a Product (General Inquiry)

**Request Body:**

```json
{
  "buyer": 123,
  "seller": 456
}
```

**Response (201 Created):**

```json
{
  "id": 2,
  "buyer": 123,
  "buyer_username": "buyer_user",
  "seller": 456,
  "seller_username": "seller_user",
  "product": null,
  "product_name": null,
  "product_image": null,
  "latest_message": null,
  "unread_count": 0,
  "created_at": "2025-11-12T10:00:00Z",
  "updated_at": "2025-11-12T10:00:00Z"
}
```

**Error Responses:**

```json
{
  "error": "A conversation already exists for this buyer-seller-product combination"
}
```

```json
{
  "product": ["Invalid pk \"999\" - object does not exist."]
}
```

---

### 3. Get Conversation Details

**Endpoint:** `GET /api/conversations/{id}/`

**Authentication:** Required (Participant only)

**Response (200 OK):**

```json
{
  "id": 1,
  "buyer": 123,
  "buyer_username": "buyer_user",
  "seller": 456,
  "seller_username": "seller_user",
  "product": 789,
  "product_name": "Handwoven Pashmina Shawl",
  "product_image": "http://localhost:8000/media/products/pashmina.jpg",
  "latest_message": {
    "id": 5,
    "sender": 456,
    "sender_username": "seller_user",
    "content": "Yes, it's available in blue!",
    "is_read": false,
    "created_at": "2025-11-12T10:45:00Z"
  },
  "unread_count": 1,
  "created_at": "2025-11-12T10:00:00Z",
  "updated_at": "2025-11-12T10:45:00Z"
}
```

**Error (403 Forbidden):**

```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 4. Update Conversation

**Endpoint:** `PUT /api/conversations/{id}/` or `PATCH /api/conversations/{id}/`

**Authentication:** Required (Participant only)

**Description:** Update conversation details. Typically used to link an existing general inquiry to a specific product after further discussion.

**Request Body:**

```json
{
  "buyer": 123,
  "seller": 456,
  "product": 789
}
```

**Use Case Example:**
```
1. Buyer sends general inquiry (conversation created with product=null)
2. Seller mentions a specific product in response
3. Update conversation to link it to that product for better context
```

**Response (200 OK):** Same as conversation object

---

### 5. Delete Conversation

**Endpoint:** `DELETE /api/conversations/{id}/`

**Authentication:** Required (Participant only)

**Response (204 No Content)**

**Note:** Deleting a conversation will also delete all associated messages.

---

### 6. Get Conversation Messages

**Endpoint:** `GET /api/conversations/{id}/messages/`

**Authentication:** Required (Participant only)

**Description:** Retrieves all messages in a conversation. Automatically marks unread messages as read for the requesting user.

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "sender": 123,
    "sender_username": "buyer_user",
    "content": "Hello! Is this shawl still available?",
    "is_read": true,
    "created_at": "2025-11-12T10:30:00Z"
  },
  {
    "id": 2,
    "sender": 456,
    "sender_username": "seller_user",
    "content": "Yes, it's available! We have it in multiple colors.",
    "is_read": true,
    "created_at": "2025-11-12T10:35:00Z"
  },
  {
    "id": 3,
    "sender": 123,
    "sender_username": "buyer_user",
    "content": "Great! Do you have it in blue?",
    "is_read": true,
    "created_at": "2025-11-12T10:40:00Z"
  },
  {
    "id": 4,
    "sender": 456,
    "sender_username": "seller_user",
    "content": "Yes, we have blue! Would you like me to reserve it for you?",
    "is_read": false,
    "created_at": "2025-11-12T10:45:00Z"
  }
]
```

**Side Effects:**
- Messages from the other participant are marked as read
- `unread_count` for the conversation is updated

---

### 7. Send Message

**Endpoint:** `POST /api/conversations/{id}/send_message/`

**Authentication:** Required (Participant only)

**Request Body:**

```json
{
  "content": "Yes, please reserve the blue one for me!"
}
```

**Response (201 Created):**

```json
{
  "id": 5,
  "sender": 123,
  "sender_username": "buyer_user",
  "content": "Yes, please reserve the blue one for me!",
  "is_read": false,
  "created_at": "2025-11-12T10:50:00Z"
}
```

**Error Responses:**

```json
{
  "error": "You are not part of this conversation"
}
```

```json
{
  "content": ["This field may not be blank."]
}
```

**Side Effects:**
- Updates conversation's `updated_at` timestamp
- Creates a notification for the recipient
- Message is marked as unread for the recipient

---

## Business Logic

### Conversation Creation & Product Linking

#### Automatic Linking
Product-linked conversations are typically created when:
- A buyer clicks "Contact Seller" on a product page
- A buyer has a question about a specific item
- System suggests contacting seller about an out-of-stock item

#### Manual Creation
Users can manually create conversations:
- Via API by providing buyer, seller, and optionally product
- General inquiries without a specific product in mind

### Product-Conversation Relationship Rules

1. **One Conversation Per Product Triplet**: Only one conversation can exist for a unique combination of buyer-seller-product
2. **Multiple Product Conversations**: Same buyer-seller pair can have multiple conversations if linked to different products
3. **Product Deletion Cascade**: Deleting a product automatically deletes associated conversations
4. **Product Validation**: When creating/updating conversations with a product:
   - Product must exist
   - Product must belong to the seller in the conversation
   - Product should not be deleted

### Message Handling

- Messages are ordered by creation time (ascending - oldest first)
- Read status is tracked per message
- When retrieving messages, unread messages from other participants are automatically marked as read
- Empty messages are not allowed
- Maximum message length: unlimited (but reasonable use recommended)

### Notifications

When a message is sent, a notification is automatically created for the recipient:
- **Type**: `message_received`
- **Title**: "New message"
- **Message**: "You have a new message from {sender_username}"
- **Product Context**: If linked to a product, notification can include product details

### Permissions

- Users can only access conversations they participate in (as buyer or seller)
- Users can only send messages to conversations they're part of
- Admin users have broader access to all conversations for moderation
- Product-linked conversations inherit product visibility rules

### Read Status

- `unread_count` represents messages from the other participant that haven't been read
- Messages are marked as read when the recipient fetches the message list
- Read status is per message, not per conversation
- Both participants can see when their messages have been read

---

## Common Use Cases

### Use Case 1: Pre-Purchase Product Inquiry

```
1. Buyer browses product listing
2. Clicks "Ask Seller" or "Contact Seller" button
3. System creates conversation linked to product
4. Buyer asks: "What's the material composition?"
5. Seller responds with details
6. Buyer makes informed purchase decision
```

**API Flow:**
```
POST /api/conversations/
{
  "buyer": 123,
  "seller": 456,
  "product": 789
}

POST /api/conversations/1/send_message/
{
  "content": "What's the material composition?"
}
```

### Use Case 2: Post-Purchase Support

```
1. Buyer receives product
2. Has question about care instructions
3. Accesses existing conversation (already linked to product)
4. Sends message asking about care
5. Seller provides care instructions
```

**API Flow:**
```
GET /api/conversations/1/messages/

POST /api/conversations/1/send_message/
{
  "content": "How should I wash this?"
}
```

### Use Case 3: General Seller Inquiry

```
1. Buyer interested in seller's shop
2. Wants to ask about custom orders
3. Creates conversation without specific product
4. Discusses custom work possibilities
5. Later links conversation to a product if order is placed
```

**API Flow:**
```
POST /api/conversations/
{
  "buyer": 123,
  "seller": 456
}

POST /api/conversations/2/send_message/
{
  "content": "Do you accept custom embroidery orders?"
}
```

### Use Case 4: Multiple Products Discussion

```
1. Buyer interested in multiple items from same seller
2. Creates separate conversation for each product
3. Each conversation maintains context of specific item
4. Clear history for each product discussion
```

**API Flow:**
```
POST /api/conversations/
{
  "buyer": 123,
  "seller": 456,
  "product": 789
}

POST /api/conversations/
{
  "buyer": 123,
  "seller": 456,
  "product": 790
}
```

---

## Error Responses

### 400 Bad Request - Duplicate Conversation

```json
{
  "non_field_errors": ["The fields buyer, seller, product must make a unique set."]
}
```

### 400 Bad Request - Empty Content

```json
{
  "content": ["This field may not be blank."]
}
```

### 403 Forbidden - Not Participant

```json
{
  "error": "You are not part of this conversation"
}
```

### 404 Not Found

```json
{
  "detail": "Not found."
}
```

### 400 Bad Request - Invalid Product

```json
{
  "product": ["Invalid pk \"999\" - object does not exist."]
}
```

---

## Usage Examples

### JavaScript (Fetch API)

#### Get Conversations with Product Context

```javascript
// Get all conversations
const response = await fetch('/api/conversations/', {
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  }
});
const conversations = await response.json();

// Filter product-specific conversations
const productConversations = conversations.results.filter(c => c.product !== null);

// Filter general inquiries
const generalInquiries = conversations.results.filter(c => c.product === null);
```

#### Create Product-Linked Conversation

```javascript
// Create conversation about a specific product
const response = await fetch('/api/conversations/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    buyer: buyerId,
    seller: sellerId,
    product: productId  // Product context
  })
});
const conversation = await response.json();
```

#### Send Product Inquiry Message

```javascript
// Send a message asking about the product
const response = await fetch(`/api/conversations/${conversationId}/send_message/`, {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: 'Hi! Is this product still available? Can you tell me more about the material?'
  })
});
const message = await response.json();
```

### Python (requests)

#### Get Product-Specific Conversations

```python
import requests

headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}

# Get all conversations
response = requests.get('/api/conversations/', headers=headers)
conversations = response.json()

# Filter conversations about a specific product
product_id = 789
product_conversations = [
    c for c in conversations['results'] 
    if c['product'] == product_id
]
```

#### Create and Send Initial Message

```python
# Create conversation linked to product
data = {
    'buyer': buyer_id,
    'seller': seller_id,
    'product': product_id
}
response = requests.post('/api/conversations/', headers=headers, json=data)
conversation = response.json()

# Send first message
message_data = {
    'content': 'Hello! I\'m interested in this product. Is it available in other colors?'
}
response = requests.post(
    f'/api/conversations/{conversation["id"]}/send_message/',
    headers=headers,
    json=message_data
)
first_message = response.json()
```

#### Update Conversation to Add Product Link

```python
# Initially created without product
conversation_id = 123

# After discussing a specific product, link it to the conversation
update_data = {
    'buyer': buyer_id,
    'seller': seller_id,
    'product': product_id  # Now linking to product
}
response = requests.put(
    f'/api/conversations/{conversation_id}/',
    headers=headers,
    json=update_data
)
updated_conversation = response.json()
```

### React/TypeScript Example

```typescript
interface Conversation {
  id: number;
  buyer: number;
  buyer_username: string;
  seller: number;
  seller_username: string;
  product: number | null;
  product_name: string | null;
  product_image: string | null;
  latest_message: Message | null;
  unread_count: number;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: number;
  sender: number;
  sender_username: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

// Fetch conversations with product context
const fetchConversations = async (): Promise<Conversation[]> => {
  const response = await fetch('/api/conversations/', {
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    }
  });
  const data = await response.json();
  return data.results;
};

// Create product-linked conversation
const createConversation = async (
  buyerId: number,
  sellerId: number,
  productId: number | null
): Promise<Conversation> => {
  const response = await fetch('/api/conversations/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      buyer: buyerId,
      seller: sellerId,
      product: productId
    })
  });
  return await response.json();
};

// Send message
const sendMessage = async (
  conversationId: number,
  content: string
): Promise<Message> => {
  const response = await fetch(
    `/api/conversations/${conversationId}/send_message/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content })
    }
  );
  return await response.json();
};
```

---

## WebSocket Integration

For real-time messaging, the platform supports WebSocket connections. Product context is included in WebSocket messages for proper routing and display.

### WebSocket Connection

```javascript
// Connect to WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws/conversations/${conversationId}/`);

// Listen for new messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New message:', data);
  
  // Data includes product context
  // {
  //   "type": "message",
  //   "conversation_id": 123,
  //   "product_id": 789,
  //   "product_name": "Handwoven Pashmina Shawl",
  //   "sender": "seller_user",
  //   "content": "Yes, it's available!",
  //   "timestamp": "2025-11-12T10:30:00Z"
  // }
};

// Send message via WebSocket
ws.send(JSON.stringify({
  "type": "message",
  "content": "Is this still available?"
}));
```

---

## Best Practices

### For Frontend Developers

1. **Display Product Context**: Always show product name and image in conversation list
2. **Separate Views**: Create distinct UI for product inquiries vs general messages
3. **Auto-Link**: When user clicks "Contact Seller" on product page, auto-create conversation with product link
4. **Smart Navigation**: Allow users to jump to product page from conversation
5. **Visual Indicators**: Show product thumbnail in message bubbles for quick reference

### For Backend Developers

1. **Validate Product-Seller**: Ensure product belongs to the seller in the conversation
2. **Handle Deletions**: Be cautious when deleting products as it cascades to conversations
3. **Index Optimization**: Create database indexes on `product` field for faster queries
4. **Archive Strategy**: Consider soft-deleting instead of hard-deleting for audit trails
5. **Notification Context**: Include product details in message notifications

### For Mobile Developers

1. **Cache Product Info**: Store product details locally to reduce API calls
2. **Image Optimization**: Use thumbnails for product images in conversation list
3. **Push Notifications**: Include product name in push notification text
4. **Deep Linking**: Enable deep links to product pages from conversations

---

## Rate Limiting

- **Standard API**: 100 requests per minute per user
- **Message Sending**: 20 messages per minute per conversation
- **Conversation Creation**: 10 new conversations per hour per user

---

## Data Retention

- Conversations are retained indefinitely unless manually deleted
- Product deletion cascades to conversations (design decision for data integrity)
- Messages remain accessible as long as the conversation exists
- Consider implementing retention policies for old conversations (e.g., 2 years after last message)

---

## Security Considerations

- All messages are stored securely with encryption at rest
- Users can only access conversations they're participants in
- Product links are validated to prevent unauthorized access
- Message content is sanitized to prevent XSS attacks
- Rate limiting prevents spam and abuse
- Admin access is logged for audit purposes

---

## Related APIs

- **Products API** (`/api/products/`): View product details for conversation context
- **Orders API** (`/api/orders/`): Access orders related to purchased products
- **Notifications API** (`/api/notifications/`): Message notifications
- **Users API** (`/api/auth/`): User information for conversation participants

---

## Troubleshooting

### Common Issues

**Q: Why can't I create a conversation?**
- Check that the product exists and belongs to the seller
- Verify that a conversation doesn't already exist for this buyer-seller-product combination
- Ensure you're authenticated

**Q: Messages not being marked as read?**
- Messages are marked as read when you call `GET /api/conversations/{id}/messages/`
- Make sure you're the recipient of the messages

**Q: Can't see product image in conversation?**
- Verify the product has images uploaded
- Check that the primary image is set
- Ensure media files are properly served

**Q: How do I handle deleted products?**
- Conversations are automatically deleted when products are deleted
- Consider archiving conversations before deleting products
- Notify users before deleting products with active conversations

---

## Future Enhancements

- **Message Search**: Search messages within conversations
- **File Attachments**: Share images and documents in messages
- **Voice Messages**: Send audio messages
- **Typing Indicators**: Show when the other person is typing
- **Message Reactions**: React to messages with emojis
- **Conversation Templates**: Pre-written messages for common questions
- **Auto-Responses**: Automatic replies for common inquiries
- **Message Translation**: Automatic translation for international buyers
- **AI Moderation**: Automatic detection of inappropriate content
- **Analytics**: Track conversation metrics and response times

---

## Changelog

- **v1.0**: Initial implementation with basic messaging
- **v1.1**: Added product linking for contextual communication
- **v1.2**: Implemented unique constraint for buyer-seller-product combinations
- **v1.3**: Added product image in conversation list
- **Current (v1.4)**: Changed from order-based to product-based conversations for better UX

---

**End of Messaging API Documentation**
