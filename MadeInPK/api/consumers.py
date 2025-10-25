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
        
        try:
            auction = AuctionListing.objects.select_related('product', 'winner').get(id=self.auction_id)
            latest_bids = auction.bids.select_related('bidder').order_by('-bid_time')[:5]
            
            return {
                'auction_id': auction.id,
                'product_name': auction.product.name,
                'current_price': str(auction.current_price),
                'status': auction.status,
                'end_time': auction.end_time.isoformat(),
                'latest_bids': [
                    {
                        'bidder': bid.bidder.username,
                        'amount': str(bid.amount),
                        'time': bid.bid_time.isoformat()
                    }
                    for bid in latest_bids
                ]
            }
        except AuctionListing.DoesNotExist:
            return {'error': 'Auction not found'}
    
    @database_sync_to_async
    def place_bid(self, auction_id, user, bid_amount):
        """Place a new bid"""
        from .models import AuctionListing, Bid
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
