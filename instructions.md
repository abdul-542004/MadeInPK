I am making backend for an app called MadeInPK. MadeInPK is a dedicated e-commerce(C2C) platform that empowers Pakistani artisans, manufacturers, and small businesses by combining fixed-price selling with real-time auctions.Unlike traditional platforms that only offer fixed prices, MadeInPK enables competitive bidding, ensuring sellers can maximize profits while buyers enjoy fair, demand-driven prices. I will be using React on frontend, Postgresql as db and DRF+django on backend. 

I want you to write django models (normalized upto BCNF) for this app. Note that I will be using Websocket for realtime bidding on auction listings. Here are the assumptions/requirements of data models:
-> One auction would contain one product only and not in bulk quanity as it would eliminate the purpose of auction(things that are auctioned are unique in nature)

-> There will also be products that are not listed in auctions but fixed price, they can be in quantity

-> A product that is in auction cannot be a fixed price product at the same time and vice versa

-> There would be a notification system (SMTP) that would notify all the users about their biddings/listings etc. Minimal celery can be setup for this i think.

-> When a bidder wins the auction, he would be sent an email in which a url would be there to redirect it to Stripe payment page. Seller would be notified upon successful transaction. 

-> Stripe Connect would be used to send money from buyer to seller with commission dropped in our platform account as platform fee (2%).

-> there would be a feedback system to track platform satisfaction and seller cooperation. Upon every successful purchase, user would be prompted to fill a form in which they would in inquired how was their experience with the seller as well as platform.

-> To connect buyer and seller so that they could deal their shipping(as our platform isnt responsible for shipping the products) there would be a minimal messaging functionality(use HTTP and not websockets).

-> To ensure that people dont see incorrect bidding on auction listing due to not refreshing page, you would implement websockets for realtime bidding.

-> for models other than auction/bidding, REST APIs would be employed.

-> There should be a system to track users that bids but not pay and it would exempt/block such users

-> addresses contraint like Lahore shouldnt be linked to Sindh province will be handled by dropboxes on frontend, Address related models can assume that the addresses are comming in right format and contraint.

-> Pay extra attention to normalisation (need data models normalized upto BCNF)

-> WE DO NOT SHIP PRODUCTS BUT JUST CONNECT BUYER AND SELLER, Seller has to ship the product himself and mark the order as shipped on his dashboard.

-> There should be a minimal complain system so the people can complain what they feel was wrong in the platform.


---
There is no Seller model and hence no seller info like seller brand name, address, biography, average rating.
No Rating and reviews for fixed price products.(auction products shouldnt have reviews and ratings)

There should also be an admin model which would allow admins  to oversee the entire platform. (See Orders, Payments, verify sellers, ban buyers/sellers, see if the products are ethical or not, etc)
