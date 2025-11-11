"""
Stripe utilities for payment processing and Stripe Connect management
"""
import stripe
from django.conf import settings
from decimal import Decimal
from .models import Payment, SellerTransfer, Order

# Initialize Stripe with secret key
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_connect_account(user, return_url, refresh_url):
    """
    Create a Stripe Connect Express account for a seller
    
    Args:
        user: User instance (seller)
        return_url: URL to return to after onboarding
        refresh_url: URL to return to if user needs to refresh
    
    Returns:
        dict with account_id and account_link_url
    """
    try:
        # Create Connect account
        account = stripe.Account.create(
            type='express',
            country='PK',  # Pakistan
            email=user.email,
            capabilities={
                'card_payments': {'requested': True},
                'transfers': {'requested': True},
            },
            business_type='individual',
            metadata={
                'user_id': user.id,
                'username': user.username,
            }
        )
        
        # Save account ID to user
        user.stripe_account_id = account.id
        user.save()
        
        # Create account link for onboarding
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=refresh_url,
            return_url=return_url,
            type='account_onboarding',
        )
        
        return {
            'account_id': account.id,
            'account_link_url': account_link.url,
        }
    
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")


def create_account_link(account_id, return_url, refresh_url):
    """
    Create a new account link for existing Connect account
    (for re-authentication or updating information)
    """
    try:
        account_link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type='account_onboarding',
        )
        return account_link.url
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")


def get_account_status(account_id):
    """
    Get the status of a Stripe Connect account
    
    Returns:
        dict with charges_enabled, payouts_enabled, and details_submitted
    """
    try:
        account = stripe.Account.retrieve(account_id)
        return {
            'charges_enabled': account.charges_enabled,
            'payouts_enabled': account.payouts_enabled,
            'details_submitted': account.details_submitted,
            'requirements': account.requirements,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")


def create_payment_intent_for_order(order, success_url, cancel_url):
    """
    Create a Stripe Payment Intent for an order
    
    For single-seller orders: Use destination charges
    For multi-seller orders: Use separate charges with application fee
    
    Args:
        order: Order instance
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is cancelled
    
    Returns:
        Payment Intent object with client_secret and checkout URL
    """
    try:
        # Convert total amount to cents (Stripe uses smallest currency unit)
        amount_cents = int(order.total_amount * 100)
        
        # Metadata for the payment
        metadata = {
            'order_id': order.id,
            'order_number': order.order_number,
            'buyer_id': order.buyer.id,
            'order_type': order.order_type,
        }
        
        # For single-seller orders (auction or direct fixed-price)
        if order.order_type in ['auction', 'fixed_price'] and order.seller:
            # Check if seller has Stripe account
            if not order.seller.stripe_account_id:
                raise Exception(f"Seller {order.seller.username} has not connected their Stripe account")
            
            # Calculate application fee (platform commission)
            application_fee_cents = int(order.platform_fee * 100)
            
            metadata['seller_id'] = order.seller.id
            
            # Create payment intent with destination charge
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='pkr',  # Pakistani Rupee
                application_fee_amount=application_fee_cents,
                transfer_data={
                    'destination': order.seller.stripe_account_id,
                },
                metadata=metadata,
                description=f"Order {order.order_number} - {order.product.name}",
            )
        
        # For multi-seller orders (cart checkout)
        elif order.order_type == 'cart':
            # For cart orders, we'll handle transfers separately after payment
            # Just create a regular payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='pkr',
                metadata=metadata,
                description=f"Order {order.order_number} - Multi-product order",
            )
        
        else:
            raise Exception("Invalid order type or missing seller information")
        
        # Create or update Payment record
        payment, created = Payment.objects.update_or_create(
            order=order,
            defaults={
                'stripe_payment_intent_id': payment_intent.id,
                'amount': order.total_amount,
                'status': 'pending',
            }
        )
        
        # Store payment intent ID in order
        order.stripe_payment_intent_id = payment_intent.id
        order.save()
        
        # Create checkout session for hosted payment page
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'pkr',
                    'product_data': {
                        'name': f"Order {order.order_number}",
                        'description': f"{order.get_order_type_display()} order",
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            payment_intent_data={
                'metadata': metadata,
            } if order.order_type == 'cart' else None,
            metadata=metadata,
        )
        
        return {
            'payment_intent_id': payment_intent.id,
            'client_secret': payment_intent.client_secret,
            'checkout_url': checkout_session.url,
        }
    
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")


def create_transfers_for_cart_order(payment):
    """
    Create transfers to sellers for a multi-seller cart order
    Called after payment is successful
    
    Args:
        payment: Payment instance for the order
    """
    order = payment.order
    
    if order.order_type != 'cart':
        return  # Only for cart orders
    
    # Group order items by seller
    from django.db.models import Sum
    from .models import OrderItem
    
    seller_amounts = OrderItem.objects.filter(order=order).values(
        'product__seller'
    ).annotate(
        total=Sum('subtotal')
    )
    
    for seller_data in seller_amounts:
        seller_id = seller_data['product__seller']
        subtotal = seller_data['total']
        
        # Calculate platform fee for this seller (2%)
        platform_fee = subtotal * Decimal('0.02')
        transfer_amount = subtotal - platform_fee
        
        # Get seller
        from .models import User
        seller = User.objects.get(id=seller_id)
        
        # Check if seller has Stripe account
        if not seller.stripe_account_id:
            # Create transfer record as failed
            SellerTransfer.objects.create(
                payment=payment,
                seller=seller,
                amount=transfer_amount,
                platform_fee=platform_fee,
                status='failed',
            )
            continue
        
        try:
            # Create transfer to seller
            transfer = stripe.Transfer.create(
                amount=int(transfer_amount * 100),  # Convert to cents
                currency='pkr',
                destination=seller.stripe_account_id,
                source_transaction=payment.stripe_payment_intent_id,
                metadata={
                    'order_id': order.id,
                    'seller_id': seller.id,
                    'payment_id': payment.id,
                }
            )
            
            # Create transfer record
            SellerTransfer.objects.create(
                payment=payment,
                seller=seller,
                amount=transfer_amount,
                platform_fee=platform_fee,
                stripe_transfer_id=transfer.id,
                status='succeeded',
            )
        
        except stripe.error.StripeError as e:
            # Create transfer record as failed
            SellerTransfer.objects.create(
                payment=payment,
                seller=seller,
                amount=transfer_amount,
                platform_fee=platform_fee,
                status='failed',
            )


def handle_payment_intent_succeeded(payment_intent):
    """
    Handle successful payment intent
    Updates order and payment status, creates transfers if needed
    """
    from django.utils import timezone
    
    try:
        # Get payment by payment intent ID
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent.id)
        order = payment.order
        
        # Update payment status
        payment.status = 'succeeded'
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update order status
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        
        # For cart orders, create transfers to sellers
        if order.order_type == 'cart':
            create_transfers_for_cart_order(payment)
        
        # Send notification to buyer
        from .models import Notification
        Notification.objects.create(
            user=order.buyer,
            notification_type='payment_received',
            title='Payment Successful',
            message=f'Your payment for order {order.order_number} has been received.',
            order=order
        )
        
        # Notify seller(s)
        sellers = order.get_sellers()
        for seller in sellers:
            Notification.objects.create(
                user=seller,
                notification_type='payment_received',
                title='Payment Received',
                message=f'Payment received for order {order.order_number}.',
                order=order
            )
        
        return True
    
    except Payment.DoesNotExist:
        return False


def handle_payment_intent_failed(payment_intent):
    """
    Handle failed payment intent
    """
    from django.utils import timezone
    
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent.id)
        order = payment.order
        
        # Update payment status
        payment.status = 'failed'
        payment.save()
        
        # Update order status
        order.status = 'payment_failed'
        order.save()
        
        # Increment failed payment count for buyer
        buyer = order.buyer
        buyer.failed_payment_count += 1
        
        # Block user if too many failed payments
        if buyer.failed_payment_count >= settings.MAX_FAILED_PAYMENTS_BEFORE_BLOCK:
            buyer.is_blocked = True
            
            # Notify user about blocking
            from .models import Notification
            Notification.objects.create(
                user=buyer,
                notification_type='account_blocked',
                title='Account Blocked',
                message='Your account has been blocked due to multiple failed payments.',
            )
        
        buyer.save()
        
        # For auction orders, track payment violation
        if order.order_type == 'auction' and order.auction:
            from .models import PaymentViolation
            PaymentViolation.objects.create(
                user=buyer,
                auction=order.auction,
                order=order,
                payment_deadline=order.payment_deadline,
                notes='Payment failed'
            )
        
        return True
    
    except Payment.DoesNotExist:
        return False
