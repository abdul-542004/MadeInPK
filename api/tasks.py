from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


@shared_task
def check_auction_endings():
    """Check for auctions that have ended and process winners"""
    from .models import AuctionListing, Order, Notification
    from decimal import Decimal
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    import uuid
    
    # Get auctions that have ended but not yet processed
    now = timezone.now()
    ended_auctions = AuctionListing.objects.filter(
        status='active',
        end_time__lte=now
    ).select_related('product', 'product__seller')
    
    channel_layer = get_channel_layer()
    
    for auction in ended_auctions:
        # Get the winning bid
        winning_bid = auction.bids.filter(is_winning=True).first()
        
        if winning_bid:
            # Update auction with winner
            auction.winner = winning_bid.bidder
            auction.status = 'ended'
            auction.save()
            
            # Create order
            total_amount = winning_bid.amount
            platform_fee = total_amount * Decimal(str(settings.STRIPE_PLATFORM_FEE_PERCENTAGE))
            seller_amount = total_amount - platform_fee
            
            # Get buyer's default shipping address
            default_address = winning_bid.bidder.addresses.filter(is_default=True).first()
            if not default_address:
                # Use any address if no default
                default_address = winning_bid.bidder.addresses.first()
            
            order = Order.objects.create(
                order_number=f"AUC-{uuid.uuid4().hex[:12].upper()}",
                buyer=winning_bid.bidder,
                seller=auction.product.seller,
                product=auction.product,
                order_type='auction',
                auction=auction,
                quantity=1,
                unit_price=winning_bid.amount,
                total_amount=total_amount,
                platform_fee=platform_fee,
                seller_amount=seller_amount,
                shipping_address=default_address,
                status='pending_payment',
                payment_deadline=now + timedelta(hours=settings.PAYMENT_DEADLINE_HOURS)
            )
            
            # Create Stripe payment URL
            try:
                from .stripe_utils import create_payment_intent_for_order
                import os
                
                base_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
                
                payment_result = create_payment_intent_for_order(
                    order=order,
                    success_url=f"{base_url}/api/payments/success/?order_id={order.id}",
                    cancel_url=f"{frontend_url}/auctions/{auction.id}?payment_cancelled=true"
                )
                
                order.payment_url = payment_result['checkout_url']
                if payment_result.get('session_id'):
                    order.stripe_payment_intent_id = payment_result['session_id']
                order.save()
            except Exception as e:
                print(f"Failed to create payment URL for auction order {order.id}: {str(e)}")
                order.payment_url = f"{frontend_url}/orders/{order.id}/payment"
                order.save()
            
            # Create notification for winner
            notification = Notification.objects.create(
                user=winning_bid.bidder,
                notification_type='auction_won',
                title='Congratulations! You won the auction',
                message=f'You won the auction for {auction.product.name}. Please complete payment within 24 hours: {order.payment_url}',
                auction=auction,
                order=order
            )
            
            # Send email notification
            send_auction_won_email.delay(order.id)
            
            # Notify seller
            Notification.objects.create(
                user=auction.product.seller,
                notification_type='auction_ended',
                title='Your auction has ended',
                message=f'Your auction for {auction.product.name} has ended. Winner: {winning_bid.bidder.username}',
                auction=auction,
                order=order
            )
            
            # Broadcast auction end to all connected WebSocket clients
            if channel_layer:
                room_group_name = f'auction_{auction.id}'
                async_to_sync(channel_layer.group_send)(
                    room_group_name,
                    {
                        'type': 'auction_ended',
                        'data': {
                            'auction_id': auction.id,
                            'status': 'ended',
                            'winner': winning_bid.bidder.username,
                            'final_price': str(winning_bid.amount),
                            'product_name': auction.product.name,
                            'message': f'Auction ended! Winner: {winning_bid.bidder.username}'
                        }
                    }
                )
        else:
            # No bids, mark as ended
            auction.status = 'ended'
            auction.save()
            
            # Notify seller
            Notification.objects.create(
                user=auction.product.seller,
                notification_type='auction_ended',
                title='Your auction has ended',
                message=f'Your auction for {auction.product.name} has ended with no bids.',
                auction=auction
            )
            
            # Broadcast auction end to all connected WebSocket clients
            if channel_layer:
                room_group_name = f'auction_{auction.id}'
                async_to_sync(channel_layer.group_send)(
                    room_group_name,
                    {
                        'type': 'auction_ended',
                        'data': {
                            'auction_id': auction.id,
                            'status': 'ended',
                            'winner': None,
                            'final_price': str(auction.current_price),
                            'product_name': auction.product.name,
                            'message': 'Auction ended with no bids'
                        }
                    }
                )


@shared_task
def check_payment_deadlines():
    """Check for orders with expired payment deadlines"""
    from .models import Order, PaymentViolation, User
    
    now = timezone.now()
    expired_orders = Order.objects.filter(
        status='pending_payment',
        payment_deadline__lte=now
    ).select_related('buyer', 'auction')
    
    for order in expired_orders:
        # Mark order as payment failed
        order.status = 'payment_failed'
        order.save()
        
        # Create payment violation record
        PaymentViolation.objects.create(
            user=order.buyer,
            auction=order.auction,
            order=order,
            payment_deadline=order.payment_deadline,
            notes='Payment deadline expired'
        )
        
        # Increment failed payment count
        buyer = order.buyer
        buyer.failed_payment_count += 1
        
        # Block user if they exceeded the limit
        if buyer.failed_payment_count >= settings.MAX_FAILED_PAYMENTS_BEFORE_BLOCK:
            buyer.is_blocked = True
            
            # Notify user about blocking
            from .models import Notification
            Notification.objects.create(
                user=buyer,
                notification_type='account_blocked',
                title='Account Blocked',
                message=f'Your account has been blocked due to {buyer.failed_payment_count} failed payments.',
            )
            
            send_account_blocked_email.delay(buyer.id)
        
        buyer.save()


@shared_task
def send_pending_notifications():
    """Send email notifications that haven't been sent yet"""
    from .models import Notification
    
    pending_notifications = Notification.objects.filter(
        is_sent_via_email=False
    ).select_related('user')[:50]  # Process 50 at a time
    
    for notification in pending_notifications:
        try:
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                fail_silently=False,
            )
            
            notification.is_sent_via_email = True
            notification.email_sent_at = timezone.now()
            notification.save()
        except Exception as e:
            print(f"Failed to send email to {notification.user.email}: {str(e)}")


@shared_task
def send_auction_won_email(order_id):
    """Send email to auction winner with payment link"""
    from .models import Order
    
    try:
        order = Order.objects.select_related('buyer', 'product', 'auction').get(id=order_id)
        
        subject = f'You won the auction for {order.product.name}'
        message = f"""
Congratulations {order.buyer.username}!

You won the auction for: {order.product.name}
Winning bid: Rs. {order.total_amount}

Please complete your payment within 24 hours using the link below:
{order.payment_url}

Order Number: {order.order_number}
Payment Deadline: {order.payment_deadline.strftime('%Y-%m-%d %H:%M:%S')}

Thank you for using MadeInPK!
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.buyer.email],
            fail_silently=False,
        )
    except Order.DoesNotExist:
        print(f"Order {order_id} not found")


@shared_task
def send_account_blocked_email(user_id):
    """Send email notification when user is blocked"""
    from .models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'MadeInPK Account Blocked'
        message = f"""
Dear {user.username},

Your MadeInPK account has been blocked due to multiple failed payments.

You have failed to complete payment for {user.failed_payment_count} auction(s) you won.

If you believe this is a mistake, please contact our support team.

Thank you,
MadeInPK Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        print(f"User {user_id} not found")


@shared_task
def send_payment_success_email(order_id):
    """Send email notifications after successful payment"""
    from .models import Order
    
    try:
        order = Order.objects.select_related('buyer', 'seller', 'product').get(id=order_id)
        
        # Email to buyer
        buyer_subject = f'Payment Successful - Order {order.order_number}'
        buyer_message = f"""
Dear {order.buyer.username},

Your payment has been successfully processed!

Order Details:
- Order Number: {order.order_number}
- Product: {order.product.name}
- Amount: Rs. {order.total_amount}

The seller will ship your item soon. You can track your order in your dashboard.

Thank you for using MadeInPK!
        """
        
        send_mail(
            subject=buyer_subject,
            message=buyer_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.buyer.email],
            fail_silently=False,
        )
        
        # Email to seller
        seller_subject = f'New Sale - Order {order.order_number}'
        seller_message = f"""
Dear {order.seller.username},

Great news! You have a new sale.

Order Details:
- Order Number: {order.order_number}
- Product: {order.product.name}
- Amount: Rs. {order.seller_amount} (after platform fee)
- Buyer: {order.buyer.username}

Please ship the item and mark it as shipped in your dashboard.

Shipping Address:
{order.shipping_address.street_address}
{order.shipping_address.city}
{order.shipping_address.postal_code}

Thank you for selling on MadeInPK!
        """
        
        send_mail(
            subject=seller_subject,
            message=seller_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.seller.email],
            fail_silently=False,
        )
    except Order.DoesNotExist:
        print(f"Order {order_id} not found")


@shared_task
def send_feedback_request_email(order_id):
    """Send feedback request after order is delivered"""
    from .models import Order
    
    try:
        order = Order.objects.select_related('buyer', 'seller', 'product').get(id=order_id)
        
        subject = f'Please provide feedback - Order {order.order_number}'
        message = f"""
Dear {order.buyer.username},

We hope you received your order for {order.product.name} in good condition.

We would love to hear about your experience with the seller and our platform.

Please take a moment to provide your feedback in your dashboard.

Thank you for using MadeInPK!
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.buyer.email],
            fail_silently=False,
        )
    except Order.DoesNotExist:
        print(f"Order {order_id} not found")


@shared_task
def send_outbid_notification_email(user_id, auction_id, new_bid_amount, product_name):
    """Send email notification when user is outbid"""
    from .models import User, AuctionListing
    
    try:
        user = User.objects.get(id=user_id)
        auction = AuctionListing.objects.select_related('product').get(id=auction_id)
        
        subject = f'You have been outbid on {product_name}'
        message = f"""
Dear {user.username},

You have been outbid on the auction for {product_name}.

New highest bid: Rs. {new_bid_amount}

If you're still interested, you can place a higher bid to regain the lead.

Log in to your MadeInPK account to view the auction and place a new bid.

Thank you for using MadeInPK!
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        print(f"User {user_id} not found")
    except AuctionListing.DoesNotExist:
        print(f"Auction {auction_id} not found")
    except Exception as e:
        print(f"Failed to send outbid email: {str(e)}")
