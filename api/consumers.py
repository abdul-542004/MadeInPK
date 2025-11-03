import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class AuctionConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time auction bidding"""
    
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.room_group_name = f'auction_{self.auction_id}'
        
        # Join auction group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current auction status
        auction_data = await self.get_auction_data()
        await self.send(text_data=json.dumps({
            'type': 'auction_status',
            'data': auction_data
        }))
    
    async def disconnect(self, close_code):
        # Leave auction group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive bid from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'place_bid':
            bid_amount = data.get('amount')
            user = self.scope.get('user')
            
            # Check if user is authenticated
            if not user or user.is_anonymous:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You must be authenticated to place a bid'
                }))
                return
            
            # Validate and place bid
            result = await self.place_bid(self.auction_id, user, bid_amount)
            
            if result['success']:
                # Broadcast new bid to all users watching this auction
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'new_bid',
                        'bid_data': result['bid_data']
                    }
                )
            else:
                # Send error only to the user who placed the bid
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result['error']
                }))
    
    async def new_bid(self, event):
        """Send new bid to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_bid',
            'data': event['bid_data']
        }))
    
    async def auction_ended(self, event):
        """Notify when auction ends"""
        await self.send(text_data=json.dumps({
            'type': 'auction_ended',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_auction_data(self):
        """Get current auction status"""
        from .models import AuctionListing, Bid
        from django.conf import settings
        
        try:
            auction = AuctionListing.objects.select_related(
                'product', 
                'product__seller',
                'product__seller__seller_profile',
                'product__category',
                'winner'
            ).prefetch_related('product__images').get(id=self.auction_id)
            
            latest_bids = auction.bids.select_related('bidder').order_by('-bid_time')[:5]
            
            # Get seller information
            seller = auction.product.seller
            seller_data = {
                'id': seller.id,
                'username': seller.username,
                'email': seller.email,
            }
            
            # Add seller profile data if exists
            if hasattr(seller, 'seller_profile'):
                profile = seller.seller_profile
                seller_data.update({
                    'brand_name': profile.brand_name,
                    'biography': profile.biography,
                    'is_verified': profile.is_verified,
                    'average_rating': str(profile.average_rating),
                    'total_feedbacks': profile.total_feedbacks,
                })
            
            # Get product images
            images = auction.product.images.all().order_by('order')
            image_urls = []
            for img in images:
                if img.image:
                    # Build full URL for image
                    image_url = img.image.url
                    if not image_url.startswith('http'):
                        # Prepend media URL if it's a relative path
                        image_url = f"{settings.MEDIA_URL}{img.image.name}" if not image_url.startswith('/') else image_url
                    image_urls.append({
                        'url': image_url,
                        'is_primary': img.is_primary,
                        'order': img.order
                    })
            
            return {
                'auction_id': auction.id,
                'product': {
                    'id': auction.product.id,
                    'name': auction.product.name,
                    'description': auction.product.description,
                    'condition': auction.product.condition,
                    'category': auction.product.category.name if auction.product.category else None,
                    'images': image_urls,
                },
                'seller': seller_data,
                'starting_price': str(auction.starting_price),
                'current_price': str(auction.current_price),
                'start_time': auction.start_time.isoformat(),
                'end_time': auction.end_time.isoformat(),
                'status': auction.status,
                'is_active': auction.is_active(),
                'winner': {
                    'id': auction.winner.id,
                    'username': auction.winner.username
                } if auction.winner else None,
                'latest_bids': [
                    {
                        'bidder': bid.bidder.username,
                        'amount': str(bid.amount),
                        'time': bid.bid_time.isoformat()
                    }
                    for bid in latest_bids
                ],
                'total_bids': auction.bids.count(),
            }
        except AuctionListing.DoesNotExist:
            return {'error': 'Auction not found'}
    
    @database_sync_to_async
    def place_bid(self, auction_id, user, bid_amount):
        """Place a new bid"""
        from .models import AuctionListing, Bid, Notification
        from decimal import Decimal
        from django.utils import timezone
        
        try:
            auction = AuctionListing.objects.select_related('product').get(id=auction_id)
            
            # Validate bid
            if not auction.is_active():
                return {'success': False, 'error': 'Auction is not active'}
            
            if user.is_blocked:
                return {'success': False, 'error': 'Your account is blocked'}
            
            bid_amount = Decimal(str(bid_amount))
            
            # Check if bid is higher than current price
            if bid_amount <= auction.current_price:
                return {'success': False, 'error': 'Bid must be higher than current price'}
            
            # Check if user is not the seller
            if auction.product.seller == user:
                return {'success': False, 'error': 'You cannot bid on your own auction'}
            
            # Get the previous winning bid before updating
            previous_winning_bid = Bid.objects.filter(
                auction=auction, 
                is_winning=True
            ).select_related('bidder').first()
            
            # Mark previous winning bid as not winning
            Bid.objects.filter(auction=auction, is_winning=True).update(is_winning=False)
            
            # Create new bid
            bid = Bid.objects.create(
                auction=auction,
                bidder=user,
                amount=bid_amount,
                is_winning=True
            )
            
            # Update auction current price
            auction.current_price = bid_amount
            auction.save()
            
            # Notify the previous highest bidder that they were outbid
            if previous_winning_bid and previous_winning_bid.bidder != user:
                # Create in-app notification
                Notification.objects.create(
                    user=previous_winning_bid.bidder,
                    notification_type='bid_outbid',
                    title='You have been outbid',
                    message=f'Someone placed a higher bid of Rs. {bid_amount} on {auction.product.name}',
                    auction=auction
                )
                
                # Send email notification asynchronously
                from .tasks import send_outbid_notification_email
                send_outbid_notification_email.delay(
                    user_id=previous_winning_bid.bidder.id,
                    auction_id=auction.id,
                    new_bid_amount=str(bid_amount),
                    product_name=auction.product.name
                )
            
            return {
                'success': True,
                'bid_data': {
                    'bidder': user.username,
                    'amount': str(bid_amount),
                    'time': bid.bid_time.isoformat(),
                    'current_price': str(auction.current_price)
                }
            }
            
        except AuctionListing.DoesNotExist:
            return {'success': False, 'error': 'Auction not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
