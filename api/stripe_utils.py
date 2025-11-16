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
    Create a Stripe Checkout Session for an order
    
    For single-seller orders: Use destination charges
    For multi-seller orders: Create regular payment, handle transfers after payment succeeds
    
    Args:
        order: Order instance
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is cancelled
    
    Returns:
        dict with payment_intent_id, client_secret, and checkout_url
    """
    try:
        # Convert total amount to cents (Stripe uses smallest currency unit)
        # Note: PKR is a zero-decimal currency, but Stripe treats it as having decimals
        amount_cents = int(order.total_amount * 100)
        
        # Metadata for the payment
        metadata = {
            'order_id': str(order.id),
            'order_number': order.order_number,
            'buyer_id': str(order.buyer.id),
            'order_type': order.order_type,
        }
        
        # Line items for checkout
        line_items = []
        
        # For single-seller orders (auction or direct fixed-price)
        if order.order_type in ['auction', 'fixed_price'] and order.seller:
            # Check if seller has Stripe account
            if not order.seller.stripe_account_id:
                raise Exception(f"Seller {order.seller.username} has not connected their Stripe account")
            
            metadata['seller_id'] = str(order.seller.id)
            
            # Create line item
            line_items.append({
                'price_data': {
                    'currency': 'pkr',
                    'product_data': {
                        'name': order.product.name if order.product else f"Order {order.order_number}",
                        'description': order.product.description if order.product else "Product order",
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            })
            
            # Calculate application fee (platform commission) in cents
            application_fee_cents = int(order.platform_fee * 100)
            
            # Create checkout session with destination charge
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata,
                payment_intent_data={
                    'application_fee_amount': application_fee_cents,
                    'transfer_data': {
                        'destination': order.seller.stripe_account_id,
                    },
                    'metadata': metadata,
                },
            )
        
        # For multi-seller orders (cart checkout)
        elif order.order_type == 'cart':
            # For cart orders, we'll handle transfers separately after payment
            # Create line item
            line_items.append({
                'price_data': {
                    'currency': 'pkr',
                    'product_data': {
                        'name': f"Order {order.order_number}",
                        'description': "Multi-product order",
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            })
            
            # Create checkout session for cart order (no destination charge)
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata,
                payment_intent_data={
                    'metadata': metadata,
                },
            )
        
        else:
            raise Exception("Invalid order type or missing seller information")
        
        # Store the checkout session ID for later reference
        # The payment_intent is created when customer begins checkout
        order.stripe_payment_intent_id = checkout_session.id  # Store session ID temporarily
        order.save()
        
        # Note: We'll update with actual payment_intent_id when webhook receives checkout.session.completed
        
        return {
            'payment_intent_id': None,  # Will be set via webhook
            'client_secret': None,  # Not needed for checkout session
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id,
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
    Idempotent - can be called multiple times safely
    """
    from django.utils import timezone
    
    try:
        # Payment intent can be either a string ID or object
        payment_intent_id = payment_intent if isinstance(payment_intent, str) else payment_intent.id
        
        # Get payment by payment intent ID
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
        order = payment.order
        
        # Check if already processed - make this idempotent
        if payment.status == 'succeeded' and order.status == 'paid':
            print(f"Payment {payment_intent_id} already processed, skipping notifications")
            return True
        
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
        
        # Send notification to buyer (only once)
        from .models import Notification
        # Check if notification already exists to prevent duplicates
        if not Notification.objects.filter(
            user=order.buyer,
            notification_type='payment_received',
            order=order
        ).exists():
            Notification.objects.create(
                user=order.buyer,
                notification_type='payment_received',
                title='Payment Successful',
                message=f'Your payment for order {order.order_number} has been received.',
                order=order
            )
        
        # Notify seller(s) (only once per seller)
        sellers = order.get_sellers()
        for seller in sellers:
            if not Notification.objects.filter(
                user=seller,
                notification_type='payment_received',
                order=order
            ).exists():
                Notification.objects.create(
                    user=seller,
                    notification_type='payment_received',
                    title='Payment Received',
                    message=f'Payment received for order {order.order_number}.',
                    order=order
                )
        
        return True
    
    except Payment.DoesNotExist:
        print(f"Payment not found for intent: {payment_intent_id}")
        return False
    except Exception as e:
        print(f"Error handling payment success: {str(e)}")
        return False


def handle_payment_intent_failed(payment_intent):
    """
    Handle failed payment intent
    """
    from django.utils import timezone
    from django.conf import settings
    
    try:
        # Payment intent can be either a string ID or object
        payment_intent_id = payment_intent if isinstance(payment_intent, str) else payment_intent.id
        
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
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
        max_failures = getattr(settings, 'MAX_FAILED_PAYMENTS_BEFORE_BLOCK', 3)
        if buyer.failed_payment_count >= max_failures:
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
        print(f"Payment not found for intent: {payment_intent_id}")
        return False
    except Exception as e:
        print(f"Error handling payment failure: {str(e)}")
        return False
