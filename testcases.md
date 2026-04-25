# Postman Test Cases for Auction / Realtime Bidding Module

This file is designed for building a Postman collection for the auction bidding module.

It focuses on the most important paths:
- auction creation
- bid placement
- bid validation failures
- outbid flow
- notifications
- basic realtime WebSocket checks

## Collection Variables

Create these collection/environment variables first:

| Variable | Example Value |
|---|---|
| `base_url` | `http://localhost:8000` |
| `ws_base_url` | `ws://localhost:8000` |
| `seller_email` | `seller_api_01@example.com` |
| `seller_password` | `Pass12345` |
| `bidder1_email` | `buyer_api_01@example.com` |
| `bidder1_password` | `Pass12345` |
| `bidder2_email` | `buyer_api_02@example.com` |
| `bidder2_password` | `Pass12345` |
| `seller_token` | |
| `bidder1_token` | |
| `bidder2_token` | |
| `category_id` | |
| `city_id` | |
| `product_id` | |
| `auction_id` | |
| `product2_id` | |
| `expired_auction_id` | |

## Setup Requests (Run once before the main tests)

These are setup requests. You can keep them in a `Setup` folder in Postman.

### S1. Register Seller

`POST {{base_url}}/api/auth/register/`

Body:

```json
{
  "username": "seller_api_01",
  "email": "{{seller_email}}",
  "password": "{{seller_password}}",
  "password_confirm": "{{seller_password}}",
  "first_name": "Seller",
  "last_name": "One",
  "phone_number": "03001234567",
  "role": "seller"
}
```

### S2. Login Seller and Save Token

`POST {{base_url}}/api/auth/login/`

Body:

```json
{
  "email": "{{seller_email}}",
  "password": "{{seller_password}}"
}
```

Tests:

```javascript
pm.test("Seller login OK", function () {
  pm.response.to.have.status(200);
});
const json = pm.response.json();
pm.collectionVariables.set("seller_token", json.token);
```

### S3. Register Bidder 1

`POST {{base_url}}/api/auth/register/`

```json
{
  "username": "buyer_api_01",
  "email": "{{bidder1_email}}",
  "password": "{{bidder1_password}}",
  "password_confirm": "{{bidder1_password}}",
  "first_name": "Buyer",
  "last_name": "One",
  "phone_number": "03002223333",
  "role": "buyer"
}
```

### S4. Login Bidder 1 and Save Token

`POST {{base_url}}/api/auth/login/`

```json
{
  "email": "{{bidder1_email}}",
  "password": "{{bidder1_password}}"
}
```

Tests:

```javascript
pm.test("Bidder1 login OK", function () {
  pm.response.to.have.status(200);
});
const json = pm.response.json();
pm.collectionVariables.set("bidder1_token", json.token);
```

### S5. Register Bidder 2

`POST {{base_url}}/api/auth/register/`

```json
{
  "username": "buyer_api_02",
  "email": "{{bidder2_email}}",
  "password": "{{bidder2_password}}",
  "password_confirm": "{{bidder2_password}}",
  "first_name": "Buyer",
  "last_name": "Two",
  "phone_number": "03004445555",
  "role": "buyer"
}
```

### S6. Login Bidder 2 and Save Token

`POST {{base_url}}/api/auth/login/`

```json
{
  "email": "{{bidder2_email}}",
  "password": "{{bidder2_password}}"
}
```

Tests:

```javascript
pm.test("Bidder2 login OK", function () {
  pm.response.to.have.status(200);
});
const json = pm.response.json();
pm.collectionVariables.set("bidder2_token", json.token);
```

---

## Main Test Cases

### TC-01 Get Categories and Save `category_id`

Request:
- Method: `GET`
- URL: `{{base_url}}/api/categories/`
- Auth: none

Tests:

```javascript
pm.test("Categories fetched", function () {
  pm.response.to.have.status(200);
});
const json = pm.response.json();
const firstCategory = json.results ? json.results[0] : json[0];
pm.expect(firstCategory).to.have.property("id");
pm.collectionVariables.set("category_id", firstCategory.id);
```

Expected result:
- `200 OK`
- At least one category returned
- `category_id` saved

### TC-02 Create Product as Seller

Request:
- Method: `POST`
- URL: `{{base_url}}/api/products/`
- Header: `Authorization: Token {{seller_token}}`
- Body: `form-data`

Body fields:
- `category`: `{{category_id}}`
- `name`: `Realtime Auction Product 01`
- `description`: `Product created for auction bidding Postman testing`
- `condition`: `new`

Tests:

```javascript
pm.test("Product created", function () {
  pm.response.to.have.status(201);
});
const json = pm.response.json();
pm.collectionVariables.set("product_id", json.id);
pm.expect(json.name).to.eql("Realtime Auction Product 01");
```

Expected result:
- `201 Created`
- product is created and `product_id` is saved

### TC-03 Create Active Auction as Seller

Request:
- Method: `POST`
- URL: `{{base_url}}/api/auctions/`
- Header: `Authorization: Token {{seller_token}}`
- Body: raw JSON

```json
{
  "product_id": {{product_id}},
  "starting_price": 1000.00,
  "start_time": "2026-04-24T10:00:00Z",
  "end_time": "2026-04-30T10:00:00Z"
}
```

Tests:

```javascript
pm.test("Auction created", function () {
  pm.response.to.have.status(201);
});
const json = pm.response.json();
pm.collectionVariables.set("auction_id", json.id);
pm.expect(json.current_price).to.eql("1000.00");
pm.expect(json.status).to.eql("active");
```

Expected result:
- `201 Created`
- `auction_id` saved
- `current_price == starting_price`

### TC-04 Get Auction Details

Request:
- Method: `GET`
- URL: `{{base_url}}/api/auctions/{{auction_id}}/`
- Auth: none

Tests:

```javascript
pm.test("Auction details fetched", function () {
  pm.response.to.have.status(200);
});
const json = pm.response.json();
pm.expect(json.id).to.eql(Number(pm.collectionVariables.get("auction_id")));
pm.expect(json.status).to.eql("active");
pm.expect(json.total_bids).to.eql(0);
```

Expected result:
- `200 OK`
- active auction returned with `0` bids

### TC-05 Place Bid Without Authentication

Request:
- Method: `POST`
- URL: `{{base_url}}/api/auctions/{{auction_id}}/place_bid/`
- Auth: none
- Body:

```json
{
  "amount": 1100.00
}
```

Tests:

```javascript
pm.test("Auth required", function () {
  pm.expect(pm.response.code).to.be.oneOf([401, 403]);
});
```

Expected result:
- request is rejected because authentication is required

### TC-06 Seller Cannot Bid on Own Auction

Request:
- Method: `POST`
- URL: `{{base_url}}/api/auctions/{{auction_id}}/place_bid/`
- Header: `Authorization: Token {{seller_token}}`
- Body:

```json
{
  "amount": 1100.00
}
```

Tests:

```javascript
pm.test("Seller own-bid rejected", function () {
  pm.response.to.have.status(400);
});
const json = pm.response.json();
pm.expect(json.error).to.eql("You cannot bid on your own auction");
```

Expected result:
- `400 Bad Request`
- seller cannot bid on own item

### TC-07 Bidder 1 Places First Valid Bid

Request:
- Method: `POST`
- URL: `{{base_url}}/api/auctions/{{auction_id}}/place_bid/`
- Header: `Authorization: Token {{bidder1_token}}`
- Body:

```json
{
  "amount": 1200.00
}
```

Tests:

```javascript
pm.test("First valid bid accepted", function () {
  pm.response.to.have.status(201);
});
const json = pm.response.json();
pm.expect(json.amount).to.eql("1200.00");
pm.expect(json.is_winning).to.eql(true);
pm.collectionVariables.set("last_bid_amount", json.amount);
```

Expected result:
- `201 Created`
- bid is winning

### TC-08 Reject Lower / Equal Bid

Request:
- Method: `POST`
- URL: `{{base_url}}/api/auctions/{{auction_id}}/place_bid/`
- Header: `Authorization: Token {{bidder1_token}}`
- Body:

```json
{
  "amount": 1200.00
}
```

Tests:

```javascript
pm.test("Low/equal bid rejected", function () {
  pm.response.to.have.status(400);
});
const json = pm.response.json();
pm.expect(json.amount[0]).to.include("Bid must be higher than current price");
```

Expected result:
- `400 Bad Request`
- serializer validation error for amount

### TC-09 Bidder 2 Outbids Bidder 1

Request:
- Method: `POST`
- URL: `{{base_url}}/api/auctions/{{auction_id}}/place_bid/`
- Header: `Authorization: Token {{bidder2_token}}`
- Body:

```json
{
  "amount": 1500.00
}
```

Tests:

```javascript
pm.test("Outbid accepted", function () {
  pm.response.to.have.status(201);
});
const json = pm.response.json();
pm.expect(json.amount).to.eql("1500.00");
pm.expect(json.is_winning).to.eql(true);
```

Expected result:
- `201 Created`
- bidder 2 becomes winning bidder

### TC-10 Get Bid History and Verify Ordering

Request:
- Method: `GET`
- URL: `{{base_url}}/api/auctions/{{auction_id}}/bids/`
- Auth: none

Tests:

```javascript
pm.test("Bid history fetched", function () {
  pm.response.to.have.status(200);
});
const json = pm.response.json();
pm.expect(json.length).to.be.at.least(2);
pm.expect(json[0].bidder_username).to.eql("buyer_api_02");
pm.expect(json[0].is_winning).to.eql(true);
pm.expect(json[1].bidder_username).to.eql("buyer_api_01");
pm.expect(json[1].is_winning).to.eql(false);
```

Expected result:
- `200 OK`
- latest bid first
- only latest highest bid has `is_winning = true`

### TC-11 Get Auction Details Again and Verify `current_price`

Request:
- Method: `GET`
- URL: `{{base_url}}/api/auctions/{{auction_id}}/`
- Auth: none

Tests:

```javascript
pm.test("Auction reflects latest price", function () {
  pm.response.to.have.status(200);
});
const json = pm.response.json();
pm.expect(json.current_price).to.eql("1500.00");
pm.expect(json.total_bids).to.eql(2);
```

Expected result:
- `current_price` matches latest successful bid
- `total_bids = 2`

### TC-12 Check Outbid Notification for Bidder 1

Request:
- Method: `GET`
- URL: `{{base_url}}/api/notifications/`
- Header: `Authorization: Token {{bidder1_token}}`

Tests:

```javascript
pm.test("Notifications fetched", function () {
  pm.response.to.have.status(200);
});
const json = pm.response.json();
const list = json.results ? json.results : json;
const notif = list.find(n => n.notification_type === "bid_outbid" && n.auction === Number(pm.collectionVariables.get("auction_id")));
pm.expect(notif).to.exist;
if (notif) {
  pm.collectionVariables.set("outbid_notification_id", notif.id);
}
```

Expected result:
- bidder 1 sees `bid_outbid` notification for this auction

### TC-13 Mark Outbid Notification as Read

Request:
- Method: `POST`
- URL: `{{base_url}}/api/notifications/{{outbid_notification_id}}/mark_read/`
- Header: `Authorization: Token {{bidder1_token}}`

Tests:

```javascript
pm.test("Notification marked read", function () {
  pm.response.to.have.status(200);
});
const json = pm.response.json();
pm.expect(json.message).to.eql("Notification marked as read");
```

Expected result:
- `200 OK`
- notification marked as read

### TC-14 Filter Seller's Auctions with `my_auctions=true`

Request:
- Method: `GET`
- URL: `{{base_url}}/api/auctions/?my_auctions=true`
- Header: `Authorization: Token {{seller_token}}`

Tests:

```javascript
pm.test("Seller auctions filtered", function () {
  pm.response.to.have.status(200);
});
const json = pm.response.json();
const list = json.results ? json.results : json;
const found = list.some(a => a.id === Number(pm.collectionVariables.get("auction_id")));
pm.expect(found).to.eql(true);
```

Expected result:
- seller sees the created auction in filtered results

### TC-15 Create Second Product for Expired-Auction Test

Request:
- Method: `POST`
- URL: `{{base_url}}/api/products/`
- Header: `Authorization: Token {{seller_token}}`
- Body: `form-data`

Body fields:
- `category`: `{{category_id}}`
- `name`: `Expired Auction Product 01`
- `description`: `Product for inactive auction validation`
- `condition`: `new`

Tests:

```javascript
pm.test("Second product created", function () {
  pm.response.to.have.status(201);
});
const json = pm.response.json();
pm.collectionVariables.set("product2_id", json.id);
```

Expected result:
- second product created

### TC-16 Create Already Expired Auction

Request:
- Method: `POST`
- URL: `{{base_url}}/api/auctions/`
- Header: `Authorization: Token {{seller_token}}`
- Body:

```json
{
  "product_id": {{product2_id}},
  "starting_price": 800.00,
  "start_time": "2026-04-20T10:00:00Z",
  "end_time": "2026-04-21T10:00:00Z"
}
```

Tests:

```javascript
pm.test("Expired-time auction created", function () {
  pm.response.to.have.status(201);
});
const json = pm.response.json();
pm.collectionVariables.set("expired_auction_id", json.id);
```

Expected result:
- auction object is created
- but it should not be active anymore when bidding is attempted

### TC-17 Try Bidding on Expired Auction

Request:
- Method: `POST`
- URL: `{{base_url}}/api/auctions/{{expired_auction_id}}/place_bid/`
- Header: `Authorization: Token {{bidder1_token}}`
- Body:

```json
{
  "amount": 900.00
}
```

Tests:

```javascript
pm.test("Inactive auction bid rejected", function () {
  pm.response.to.have.status(400);
});
const json = pm.response.json();
pm.expect(json.error).to.eql("Auction is not active");
```

Expected result:
- `400 Bad Request`
- bid blocked because auction is inactive by time

### TC-18 Realtime WebSocket Smoke Test

This one is best kept in a `WebSocket` folder in Postman.

#### WS-1 Connect to Auction Channel

Request:
- Type: WebSocket
- URL: `{{ws_base_url}}/ws/auction/{{auction_id}}/?token={{bidder1_token}}`

Expected result:
- socket connects successfully
- first server message has:
  - `"type": "auction_status"`
  - current price
  - latest bids
  - seller/product info

#### WS-2 Broadcast New Bid

1. Open the above WebSocket for bidder 1.
2. Open another WebSocket or use REST with bidder 2 to place a higher bid.
3. Bidder 1 socket should receive:

```json
{
  "type": "new_bid",
  "data": {
    "bidder": "buyer_api_02",
    "amount": "1600.00"
  }
}
```

If using WebSocket to place the bid, send:

```json
{
  "type": "place_bid",
  "amount": 1600.00
}
```

Expected result:
- all connected clients on the same auction receive `new_bid`
- updated bid amount matches the newly placed bid

---

## Suggested Folder Order in Postman

1. `Setup`
2. `Auction REST Tests`
3. `Notifications`
4. `Realtime WebSocket`

## Notes

- Use `Authorization: Token {{token}}` for authenticated REST requests.
- For product creation, use `form-data` in Postman.
- For auction creation and bid placement, use raw JSON.
- The WebSocket auth for this project uses `?token=...` in the query string.
- If seeded data differs in your DB, just use the first valid category returned by `GET /api/categories/`.
