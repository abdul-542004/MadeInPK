from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from django.utils import timezone
from decimal import Decimal
from dateutil import parser
import uuid

from .models import (
    Province, City, Address, Category, Product, ProductImage,
    AuctionListing, Bid, FixedPriceListing, Order, Payment,
    Feedback, Conversation, Message, Notification, Complaint, Wishlist, SellerProfile, ProductReview,
    Cart, CartItem, OrderItem, SellerTransfer
)
from .serializers import (
    UserRegistrationSerializer, UserSerializer, UserProfileSerializer,
    ProvinceSerializer, CitySerializer, AddressSerializer,
    CategorySerializer, ProductSerializer, ProductCreateSerializer,
    ProductImageSerializer, AuctionListingSerializer, AuctionCreateSerializer,
    BidSerializer, BidCreateSerializer, FixedPriceListingSerializer,
    FixedPriceCreateSerializer, OrderSerializer, OrderCreateSerializer,
    PaymentSerializer, FeedbackSerializer, FeedbackCreateSerializer,
    MessageSerializer, ConversationSerializer, NotificationSerializer,
    ComplaintSerializer, ComplaintCreateSerializer, WishlistSerializer, WishlistCreateSerializer, 
    SellerProfileSerializer, ProductReviewSerializer, ProductReviewCreateSerializer,
    BecomeSellerSerializer, CartSerializer, CartItemSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, CartCheckoutSerializer, OrderItemSerializer, SellerTransferSerializer,
    SellerEarningsSerializer, SellerTransactionSerializer, ProductPerformanceSerializer
)
from .stripe_utils import (
    create_stripe_connect_account, create_account_link, get_account_status,
    create_payment_intent_for_order
)

User = get_user_model()


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        # Create welcome notification
        Notification.objects.create(
            user=user,
            notification_type='general',
            title='Welcome to MadeInPK!',
            message='Thank you for registering. Start exploring our platform and discover amazing products from local sellers!'
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(username=email, password=password)
    if user:
        if user.is_blocked:
            return Response({'error': 'Your account is blocked'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })
    return Response({'error': 'Invalid credentials'}, 
                   status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout"""
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'})


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get or update current user profile"""
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    # PUT or PATCH - update profile
    partial = request.method == 'PATCH'
    serializer = UserSerializer(request.user, data=request.data, partial=partial)
    
    if serializer.is_valid():
        serializer.save()
        # Return full profile data
        profile_serializer = UserProfileSerializer(request.user)
        return Response(profile_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def become_seller(request):
    """Allows a buyer to upgrade to seller role and create seller profile"""
    
    if request.method == 'GET':
        # Check if user can become a seller
        user = request.user
        can_become_seller = user.role == 'buyer' and not hasattr(user, 'seller_profile')
        
        return Response({
            'can_become_seller': can_become_seller,
            'current_role': user.role,
            'has_seller_profile': hasattr(user, 'seller_profile'),
            'message': 'You can upgrade to seller' if can_become_seller else 'You already have seller capabilities or a seller profile'
        })
    
    # POST request - upgrade to seller
    serializer = BecomeSellerSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        result = serializer.save()
        
        # Create notification for user
        Notification.objects.create(
            user=result['user'],
            notification_type='general',
            title='Welcome to Selling on MadeInPK!',
            message='Your seller account has been created successfully. You can now start listing products for sale.'
        )
        
        return Response({
            'message': 'Successfully upgraded to seller',
            'user': UserSerializer(result['user']).data,
            'seller_profile': SellerProfileSerializer(result['seller_profile']).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Location ViewSets
class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    """List provinces"""
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [AllowAny]


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """List cities, optionally filtered by province"""
    queryset = City.objects.select_related('province').all()
    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        province_id = self.request.query_params.get('province')
        if province_id:
            queryset = queryset.filter(province_id=province_id)
        return queryset


class AddressViewSet(viewsets.ModelViewSet):
    """CRUD operations for user addresses"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).select_related('city__province')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set address as default"""
        address = self.get_object()
        Address.objects.filter(user=request.user).update(is_default=False)
        address.is_default = True
        address.save()
        return Response({'message': 'Default address updated'})


# Category ViewSet
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """List product categories"""
    queryset = Category.objects.filter(parent=None)  # Root categories only
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


# Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    """CRUD operations for products"""
    queryset = Product.objects.select_related('seller', 'category').prefetch_related('images').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by seller
        seller_id = self.request.query_params.get('seller')
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by condition
        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # Filter by province (based on seller's business address or default address)
        province_id = self.request.query_params.get('province')
        if province_id:
            # Filter by sellers who have business address in the specified province
            # OR sellers who have default address in the specified province
            queryset = queryset.filter(
                Q(seller__seller_profile__business_address_id__city__province_id=province_id) |
                Q(seller__addresses__city__province_id=province_id, seller__addresses__is_default=True)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_image(self, request, pk=None):
        """Add image to product"""
        product = self.get_object()
        
        if product.seller != request.user:
            return Response({'error': 'You can only add images to your own products'},
                          status=status.HTTP_403_FORBIDDEN)
        
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': 'No image file provided'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create product image
        product_image = ProductImage.objects.create(
            product=product,
            image=image_file,
            is_primary=not product.images.exists(),  # First image is primary
            order=product.images.count()
        )
        
        serializer = ProductImageSerializer(product_image, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='delete_image/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        """Delete a product image"""
        product = self.get_object()
        
        if product.seller != request.user:
            return Response({'error': 'You can only delete images from your own products'},
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            product_image = ProductImage.objects.get(id=image_id, product=product)
        except ProductImage.DoesNotExist:
            return Response({'error': 'Image not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Don't allow deleting the only image
        if product.images.count() <= 1:
            return Response({'error': 'Product must have at least one image'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # If deleting primary image, make another image primary
        was_primary = product_image.is_primary
        product_image.delete()
        
        if was_primary:
            first_image = product.images.first()
            if first_image:
                first_image.is_primary = True
                first_image.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
# Auction ViewSet
class AuctionListingViewSet(viewsets.ModelViewSet):
    """CRUD operations for auction listings"""
    queryset = AuctionListing.objects.select_related(
        'product__seller', 'product__category', 'winner'
    ).prefetch_related('product__images', 'bids').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'product__description']
    ordering_fields = ['end_time', 'current_price', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AuctionCreateSerializer
        return AuctionListingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by seller
        seller_id = self.request.query_params.get('seller')
        if seller_id:
            queryset = queryset.filter(product__seller_id=seller_id)
        
        # Check if filtering for current authenticated user's auctions
        my_auctions = self.request.query_params.get('my_auctions')
        if my_auctions and self.request.user.is_authenticated:
            queryset = queryset.filter(product__seller=self.request.user)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(product__category_id=category_id)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def place_bid(self, request, pk=None):
        """Place a bid on an auction"""
        auction = self.get_object()
        
        # Validation
        if not auction.is_active():
            return Response({'error': 'Auction is not active'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.is_blocked:
            return Response({'error': 'Your account is blocked'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if auction.product.seller == request.user:
            return Response({'error': 'You cannot bid on your own auction'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BidCreateSerializer(
            data=request.data,
            context={'request': request, 'auction': auction}
        )
        
        if serializer.is_valid():
            bid = serializer.save()
            
            # Create notification for previous highest bidder
            previous_bid = auction.bids.filter(is_winning=False).order_by('-bid_time').first()
            if previous_bid:
                Notification.objects.create(
                    user=previous_bid.bidder,
                    notification_type='bid_outbid',
                    title='You have been outbid',
                    message=f'Someone placed a higher bid on {auction.product.name}',
                    auction=auction
                )
            
            return Response(BidSerializer(bid).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def bids(self, request, pk=None):
        """Get all bids for an auction"""
        auction = self.get_object()
        bids = auction.bids.select_related('bidder').order_by('-bid_time')
        serializer = BidSerializer(bids, many=True)
        return Response(serializer.data)


# Fixed Price Listing ViewSet
class FixedPriceListingViewSet(viewsets.ModelViewSet):
    """CRUD operations for fixed price listings"""
    queryset = FixedPriceListing.objects.select_related(
        'product__seller', 'product__category'
    ).prefetch_related('product__images').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'product__description']
    ordering_fields = ['price', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FixedPriceCreateSerializer
        return FixedPriceListingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Check if filtering for current authenticated user's listings
        my_listings = self.request.query_params.get('my_listings')
        if my_listings and self.request.user.is_authenticated:
            queryset = queryset.filter(product__seller=self.request.user)
        
        # Filter by seller
        seller_id = self.request.query_params.get('seller')
        if seller_id:
            queryset = queryset.filter(product__seller_id=seller_id)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(product__category_id=category_id)
        
        # Filter by province
        province_id = self.request.query_params.get('province')
        if province_id:
            queryset = queryset.filter(
                Q(product__seller__seller_profile__business_address_id__city__province_id=province_id) |
                Q(product__seller__addresses__city__province_id=province_id, product__seller__addresses__is_default=True)
            ).distinct()
        
        # Price range filter
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Featured filter
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(featured=True)
        elif featured == 'false':
            queryset = queryset.filter(featured=False)
        
        return queryset
    
    def update(self, request, *args, **kwargs):
        """Update listing - only seller can modify"""
        listing = self.get_object()
        if listing.product.seller != request.user:
            return Response(
                {'error': 'You can only update your own listings'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Partially update listing - only seller can modify discount fields"""
        listing = self.get_object()
        if listing.product.seller != request.user:
            return Response(
                {'error': 'You can only update your own listings'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate discount fields if being updated
        discount_fields = ['discount_percentage', 'discount_start_date', 'discount_end_date']
        discount_data = {k: v for k, v in request.data.items() if k in discount_fields}
        
        if discount_data:
            # If updating any discount field, validate the complete discount setup
            discount_percentage = discount_data.get('discount_percentage') or listing.discount_percentage
            discount_start_date = discount_data.get('discount_start_date') or listing.discount_start_date
            discount_end_date = discount_data.get('discount_end_date') or listing.discount_end_date
            
            if any([discount_percentage, discount_start_date, discount_end_date]):
                if not all([discount_percentage, discount_start_date, discount_end_date]):
                    return Response(
                        {'error': 'If setting a discount, you must provide all discount fields: '
                                 'discount_percentage, discount_start_date, and discount_end_date'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Parse dates if they're strings
                from dateutil import parser
                if isinstance(discount_start_date, str):
                    discount_start_date = parser.parse(discount_start_date)
                if isinstance(discount_end_date, str):
                    discount_end_date = parser.parse(discount_end_date)
                
                if discount_end_date <= discount_start_date:
                    return Response(
                        {'error': 'Discount end date must be after start date'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        return super().partial_update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        """Purchase a fixed price listing"""
        listing = self.get_object()
        
        if listing.status != 'active':
            return Response({'error': 'Listing is not active'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.is_blocked:
            return Response({'error': 'Your account is blocked'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if listing.product.seller == request.user:
            return Response({'error': 'You cannot purchase your own listing'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        quantity = request.data.get('quantity', 1)
        shipping_address_id = request.data.get('shipping_address')
        
        if listing.quantity < quantity:
            return Response({'error': 'Not enough quantity available'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Get shipping address
        try:
            shipping_address = Address.objects.get(id=shipping_address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({'error': 'Invalid shipping address'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create order using current price (with discount if applicable)
        current_price = listing.get_current_price()
        total_amount = current_price * quantity
        platform_fee = total_amount * Decimal('0.02')
        seller_amount = total_amount - platform_fee
        
        order = Order.objects.create(
            order_number=f"FXD-{uuid.uuid4().hex[:12].upper()}",
            buyer=request.user,
            seller=listing.product.seller,
            product=listing.product,
            order_type='fixed_price',
            fixed_price_listing=listing,
            quantity=quantity,
            unit_price=current_price,  # Use current price with discount
            total_amount=total_amount,
            platform_fee=platform_fee,
            seller_amount=seller_amount,
            shipping_address=shipping_address,
            status='pending_payment',
            payment_deadline=timezone.now() + timezone.timedelta(hours=24)
        )
        
        # Reduce listing quantity
        listing.reduce_quantity(quantity)
        
        # TODO: Create Stripe payment intent and get payment URL
        # order.payment_url = create_stripe_payment_intent(order)
        order.payment_url = f"http://localhost:8000/api/payments/{order.id}/checkout/"
        order.save()
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            notification_type='payment_reminder',
            title='Complete your payment',
            message=f'Please complete payment for {listing.product.name}',
            order=order
        )
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_status(self, request, pk=None):
        """Toggle listing status between active and inactive"""
        listing = self.get_object()
        
        # Check if user owns this listing
        if listing.product.seller != request.user:
            return Response(
                {'error': 'You do not have permission to modify this listing'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Toggle between active and inactive (don't touch out_of_stock)
        if listing.status == 'active':
            listing.status = 'inactive'
            message = 'Listing deactivated successfully'
        elif listing.status == 'inactive':
            listing.status = 'active'
            message = 'Listing activated successfully'
        elif listing.status == 'out_of_stock':
            return Response(
                {'error': 'Cannot activate out-of-stock listing. Please update the stock first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        listing.save()
        
        return Response({
            'message': message,
            'status': listing.status
        }, status=status.HTTP_200_OK)


# Order ViewSet
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """View orders"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        # Filter by role (purchases or sales)
        role = self.request.query_params.get('role')
        
        if role == 'buyer':
            # Buyer sees all orders where they are the buyer
            queryset = Order.objects.filter(buyer=user)
        elif role == 'seller':
            # Seller sees:
            # 1. Single-seller orders where they are the seller
            # 2. Multi-seller cart orders where they have items (via OrderItems)
            queryset = Order.objects.filter(
                Q(seller=user) |  # Single-seller orders
                Q(items__product__seller=user)  # Multi-seller cart orders
            ).distinct()
        else:
            # Default: Users can see orders where they are buyer or seller
            # This includes both single-seller and multi-seller orders
            queryset = Order.objects.filter(
                Q(buyer=user) |
                Q(seller=user) |
                Q(items__product__seller=user)  # Include cart orders where user is a seller
            ).distinct()
        
        queryset = queryset.select_related(
            'buyer', 'seller', 'product', 'shipping_address__city__province'
        ).prefetch_related('items__product')
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_shipped(self, request, pk=None):
        """Mark order as shipped (seller only)
        For single-seller orders: marks entire order as shipped
        For multi-seller orders: this endpoint is not applicable (not implemented yet)
        """
        order = self.get_object()
        
        # Check if this is a multi-seller order
        if order.is_multi_seller():
            return Response({
                'error': 'Multi-seller cart orders cannot be marked as shipped directly. '
                        'Each seller must ship their items individually.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Single-seller order validation
        if order.seller != request.user:
            return Response({'error': 'Only seller can mark as shipped'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if order.status != 'paid':
            return Response({'error': 'Order must be paid first'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'shipped'
        order.shipped_at = timezone.now()
        order.save()
        
        # Notify buyer
        Notification.objects.create(
            user=order.buyer,
            notification_type='order_shipped',
            title='Your order has been shipped',
            message=f'Your order {order.order_number} has been shipped',
            order=order
        )
        
        return Response({'message': 'Order marked as shipped'})
    
    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """Mark order as delivered (buyer only)"""
        order = self.get_object()
        
        if order.buyer != request.user:
            return Response({'error': 'Only buyer can mark as delivered'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if order.status != 'shipped':
            return Response({'error': 'Order must be shipped first'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'delivered'
        order.delivered_at = timezone.now()
        order.save()
        
        # Notify seller(s)
        if order.is_multi_seller():
            # Notify all sellers involved in the cart order
            sellers = order.get_sellers()
            for seller in sellers:
                Notification.objects.create(
                    user=seller,
                    notification_type='order_delivered',
                    title='Order delivered',
                    message=f'Order {order.order_number} has been delivered',
                    order=order
                )
        else:
            # Notify single seller
            if order.seller:
                Notification.objects.create(
                    user=order.seller,
                    notification_type='order_delivered',
                    title='Order delivered',
                    message=f'Order {order.order_number} has been delivered',
                    order=order
                )
        
        # Request feedback
        Notification.objects.create(
            user=order.buyer,
            notification_type='feedback_request',
            title='Please provide feedback',
            message=f'Share your experience with order {order.order_number}',
            order=order
        )
        
        return Response({'message': 'Order marked as delivered'})


# Feedback ViewSet
class FeedbackViewSet(viewsets.ModelViewSet):
    """CRUD operations for feedback"""
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Feedback.objects.select_related('buyer', 'seller', 'order').all()
        
        # Filter by seller to get seller's feedback
        seller_id = self.request.query_params.get('seller')
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackCreateSerializer
        return FeedbackSerializer
    
    def create(self, request, *args, **kwargs):
        """Create feedback for an order"""
        order_id = request.data.get('order_id')
        
        try:
            order = Order.objects.get(id=order_id, buyer=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or you are not the buyer'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if order.status != 'delivered':
            return Response({'error': 'Order must be delivered before feedback'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if hasattr(order, 'feedback'):
            return Response({'error': 'Feedback already submitted'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                order=order,
                buyer=request.user,
                seller=order.seller
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def seller_stats(self, request):
        """Get seller's average ratings"""
        seller_id = request.query_params.get('seller_id')
        if not seller_id:
            return Response({'error': 'seller_id required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        feedbacks = Feedback.objects.filter(seller_id=seller_id)
        
        if not feedbacks.exists():
            return Response({'message': 'No feedback yet'})
        
        stats = {
            'total_feedbacks': feedbacks.count(),
            'average_seller_rating': feedbacks.aggregate(Avg('seller_rating'))['seller_rating__avg'],
            'average_communication': feedbacks.aggregate(Avg('communication_rating'))['communication_rating__avg'],
            'average_shipping': feedbacks.aggregate(Avg('shipping_speed_rating'))['shipping_speed_rating__avg'],
            'product_as_described_percent': (
                feedbacks.filter(product_as_described=True).count() / feedbacks.count() * 100
            )
        }
        
        return Response(stats)


# Conversation & Message ViewSet
class ConversationViewSet(viewsets.ModelViewSet):
    """CRUD operations for conversations"""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related('buyer', 'seller', 'product').prefetch_related('messages', 'product__images')
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in a conversation"""
        conversation = self.get_object()
        messages = conversation.messages.select_related('sender').all()
        
        # Mark messages as read
        messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a conversation"""
        conversation = self.get_object()
        
        # Check if user is part of conversation
        if request.user not in [conversation.buyer, conversation.seller]:
            return Response({'error': 'You are not part of this conversation'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(
                conversation=conversation,
                sender=request.user
            )
            
            # Update conversation timestamp
            conversation.updated_at = timezone.now()
            conversation.save()
            
            # Notify recipient
            recipient = conversation.seller if request.user == conversation.buyer else conversation.buyer
            Notification.objects.create(
                user=recipient,
                notification_type='message_received',
                title='New message',
                message=f'You have a new message from {request.user.username}'
            )
            
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Notification ViewSet
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """View notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})


# Complaint ViewSet
class ComplaintViewSet(viewsets.ModelViewSet):
    """CRUD operations for complaints"""
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user).select_related(
            'order', 'seller'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ComplaintCreateSerializer
        return ComplaintSerializer


# Wishlist ViewSet
class WishlistViewSet(viewsets.ModelViewSet):
    """CRUD operations for user wishlists"""
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related(
            'product__seller', 'product__category'
        ).prefetch_related('product__images')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WishlistCreateSerializer
        return WishlistSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def remove_from_wishlist(self, request, pk=None):
        """Remove product from wishlist"""
        wishlist_item = self.get_object()
        wishlist_item.delete()
        return Response({'message': 'Product removed from wishlist'})


# Seller Profile ViewSet
class SellerProfileViewSet(viewsets.ModelViewSet):
    """CRUD operations for seller profiles"""
    serializer_class = SellerProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Admins can see all profiles, sellers can see their own
        if self.request.user.role == 'admin':
            return SellerProfile.objects.select_related('user').all()
        return SellerProfile.objects.filter(user=self.request.user).select_related('user')
    
    def perform_create(self, serializer):
        # Only allow creating profile for own user, and only if seller role
        if self.request.user.role not in ['seller', 'both']:
            raise serializers.ValidationError("Only sellers can create seller profiles")
        if hasattr(self.request.user, 'seller_profile'):
            raise serializers.ValidationError("Seller profile already exists")
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def verify(self, request, pk=None):
        """Admin action to verify seller"""
        if request.user.role != 'admin':
            return Response({'error': 'Only admins can verify sellers'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        profile = self.get_object()
        profile.is_verified = True
        profile.save()
        return Response({'message': 'Seller verified successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unverify(self, request, pk=None):
        """Admin action to unverify seller"""
        if request.user.role != 'admin':
            return Response({'error': 'Only admins can unverify sellers'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        profile = self.get_object()
        profile.is_verified = False
        profile.save()
        return Response({'message': 'Seller unverified'})


# Product Review ViewSet
class ProductReviewViewSet(viewsets.ModelViewSet):
    """CRUD operations for product reviews (fixed-price products only)"""
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = ProductReview.objects.select_related('product', 'buyer', 'order').all()
        
        # Filter by product
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by rating
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Filter verified purchases only
        verified_only = self.request.query_params.get('verified_only')
        if verified_only == 'true':
            queryset = queryset.filter(is_verified_purchase=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductReviewCreateSerializer
        return ProductReviewSerializer
    
    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)
    
    def perform_update(self, serializer):
        # Only allow updating own reviews
        review = self.get_object()
        if review.buyer != self.request.user:
            raise serializers.ValidationError("You can only update your own reviews")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow deleting own reviews
        if instance.buyer != self.request.user:
            raise serializers.ValidationError("You can only delete your own reviews")
        instance.delete()


# Shopping Cart ViewSet
class CartViewSet(viewsets.ViewSet):
    """Shopping cart operations"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        serializer = AddToCartSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        listing_id = serializer.validated_data['listing_id']
        quantity = serializer.validated_data['quantity']
        
        listing = FixedPriceListing.objects.get(id=listing_id)
        
        # Check if item already in cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            listing=listing,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            # Update quantity if item already exists
            new_quantity = cart_item.quantity + quantity
            if new_quantity > listing.quantity:
                return Response(
                    {'error': f'Only {listing.quantity} items available in stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()
        
        return Response(
            CartItemSerializer(cart_item, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['patch'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """Update cart item quantity"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UpdateCartItemSerializer(
            data=request.data,
            context={'request': request, 'cart_item': cart_item}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()
        
        return Response(CartItemSerializer(cart_item, context={'request': request}).data)
    
    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """Remove item from cart"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            return Response({'message': 'Item removed from cart'})
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response({'message': 'Cart cleared'})
        except Cart.DoesNotExist:
            return Response({'message': 'Cart is already empty'})
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Checkout cart and create order"""
        serializer = CartCheckoutSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        cart = request.user.cart
        shipping_address_id = serializer.validated_data['shipping_address_id']
        shipping_address = Address.objects.get(id=shipping_address_id)
        
        # Calculate total amounts
        total_amount = cart.get_total_price()
        platform_fee = total_amount * Decimal('0.02')
        
        # Create order
        order = Order.objects.create(
            order_number=f"CART-{uuid.uuid4().hex[:12].upper()}",
            buyer=request.user,
            order_type='cart',
            total_amount=total_amount,
            platform_fee=platform_fee,
            shipping_address=shipping_address,
            status='pending_payment',
            payment_deadline=timezone.now() + timezone.timedelta(hours=24)
        )
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.listing.product,
                listing=cart_item.listing,
                quantity=cart_item.quantity,
                unit_price=cart_item.listing.get_current_price(),
            )
            
            # Reduce listing quantity
            cart_item.listing.reduce_quantity(cart_item.quantity)
        
        # Create Stripe payment intent
        try:
            base_url = request.build_absolute_uri('/')[:-1]
            payment_result = create_payment_intent_for_order(
                order=order,
                success_url=f"{base_url}/api/payments/success/?order_id={order.id}",
                cancel_url=f"{base_url}/api/payments/cancel/?order_id={order.id}"
            )
            
            order.payment_url = payment_result['checkout_url']
            order.save()
            
        except Exception as e:
            order.delete()  # Rollback order creation
            return Response(
                {'error': f'Payment creation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Clear cart after successful order creation
        cart.items.all().delete()
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            notification_type='payment_reminder',
            title='Complete your payment',
            message=f'Please complete payment for order {order.order_number}',
            order=order
        )
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


# Stripe Connect ViewSet
class StripeConnectViewSet(viewsets.ViewSet):
    """Stripe Connect account management for sellers"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_account(self, request):
        """Create Stripe Connect account for seller"""
        user = request.user
        
        # Check if user is a seller
        if user.role not in ['seller', 'both']:
            return Response(
                {'error': 'Only sellers can create Stripe Connect accounts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if already has account
        if user.stripe_account_id:
            return Response(
                {'error': 'Stripe account already exists', 'account_id': user.stripe_account_id},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            base_url = request.build_absolute_uri('/')[:-1]
            return_url = f"{base_url}/api/stripe/connect/return/"
            refresh_url = f"{base_url}/api/stripe/connect/refresh/"
            
            result = create_stripe_connect_account(user, return_url, refresh_url)
            
            return Response({
                'message': 'Stripe Connect account created',
                'account_id': result['account_id'],
                'onboarding_url': result['account_link_url']
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def account_status(self, request):
        """Get Stripe Connect account status"""
        user = request.user
        
        if not user.stripe_account_id:
            return Response({'error': 'No Stripe account found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            status_info = get_account_status(user.stripe_account_id)
            return Response(status_info)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def refresh_onboarding(self, request):
        """Get new onboarding link for existing account"""
        user = request.user
        
        if not user.stripe_account_id:
            return Response({'error': 'No Stripe account found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            base_url = request.build_absolute_uri('/')[:-1]
            return_url = f"{base_url}/api/stripe/connect/return/"
            refresh_url = f"{base_url}/api/stripe/connect/refresh/"
            
            onboarding_url = create_account_link(user.stripe_account_id, return_url, refresh_url)
            
            return Response({'onboarding_url': onboarding_url})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def return_page(self, request):
        """Return page after Stripe onboarding"""
        return Response({
            'message': 'Stripe account setup completed',
            'status': 'success'
        })
    
    @action(detail=False, methods=['get'])
    def refresh_page(self, request):
        """Refresh page during Stripe onboarding"""
        return Response({
            'message': 'Please complete your Stripe account setup',
            'status': 'pending'
        })


# Stripe Webhook Handler
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    import stripe
    from django.conf import settings
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle different event types
    from .stripe_utils import handle_payment_intent_succeeded, handle_payment_intent_failed
    
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_intent_succeeded(payment_intent)
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_intent_failed(payment_intent)
    
    elif event['type'] == 'account.updated':
        account = event['data']['object']
        # Update seller account status if needed
        try:
            user = User.objects.get(stripe_account_id=account['id'])
            # You can store additional account info here if needed
        except User.DoesNotExist:
            pass
    
    return Response({'status': 'success'})


# Payment success and cancel pages
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_success(request):
    """Payment success page"""
    order_id = request.query_params.get('order_id')
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id, buyer=request.user)
            return Response({
                'message': 'Payment successful',
                'order': OrderSerializer(order).data
            })
        except Order.DoesNotExist:
            pass
    
    return Response({'message': 'Payment successful'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_cancel(request):
    """Payment cancelled page"""
    order_id = request.query_params.get('order_id')
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id, buyer=request.user)
            return Response({
                'message': 'Payment cancelled',
                'order': OrderSerializer(order).data,
                'payment_url': order.payment_url
            })
        except Order.DoesNotExist:
            pass
    
    return Response({'message': 'Payment cancelled'})


# Seller Statistics Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_statistics(request):
    """Get seller dashboard statistics"""
    user = request.user
    
    # Check if user is a seller
    if user.role not in ['seller', 'both']:
        return Response(
            {'error': 'Only sellers can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get seller's products
    total_products = Product.objects.filter(seller=user).count()
    
    # Get active auctions
    active_auctions = AuctionListing.objects.filter(
        product__seller=user,
        status='active'
    ).count()
    
    # Get seller's orders (as seller)
    seller_orders = Order.objects.filter(seller=user)
    total_orders = seller_orders.count()
    
    # Get pending orders (paid but not shipped)
    pending_orders = seller_orders.filter(status='paid').count()
    
    # Calculate total revenue (from completed/delivered orders)
    from decimal import Decimal
    from django.db.models import Sum
    total_revenue = seller_orders.filter(
        status__in=['paid', 'shipped', 'delivered']
    ).aggregate(
        total=Sum('seller_amount')
    )['total'] or Decimal('0.00')
    
    # Count total sales (delivered orders)
    total_sales = seller_orders.filter(status='delivered').count()
    
    return Response({
        'total_sales': total_sales,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': str(total_revenue),
        'total_products': total_products,
        'active_auctions': active_auctions,
    })


# Seller Earnings Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_earnings(request):
    """Get detailed seller earnings data for dashboard"""
    from django.db.models import Sum, Count, Q
    from datetime import datetime, timedelta
    from decimal import Decimal
    import calendar
    
    user = request.user
    
    # Check if user is a seller
    if user.role not in ['seller', 'both']:
        return Response(
            {'error': 'Only sellers can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    now = timezone.now()
    
    # Get all seller orders (including multi-seller orders via OrderItems)
    # For single-seller orders
    single_seller_orders = Order.objects.filter(
        seller=user,
        status__in=['paid', 'shipped', 'delivered']
    )
    
    # For multi-seller orders (cart orders)
    multi_seller_orders = OrderItem.objects.filter(
        product__seller=user,
        order__status__in=['paid', 'shipped', 'delivered']
    )
    
    # Calculate current month earnings
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_single = single_seller_orders.filter(
        paid_at__gte=current_month_start
    ).aggregate(total=Sum('seller_amount'))['total'] or Decimal('0.00')
    
    current_month_multi = multi_seller_orders.filter(
        order__paid_at__gte=current_month_start
    ).aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
    # Apply platform fee reduction (2%)
    current_month_multi = current_month_multi * Decimal('0.98')
    
    current_month_earnings = current_month_single + current_month_multi
    
    # Calculate last month earnings
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = current_month_start
    
    last_month_single = single_seller_orders.filter(
        paid_at__gte=last_month_start,
        paid_at__lt=last_month_end
    ).aggregate(total=Sum('seller_amount'))['total'] or Decimal('0.00')
    
    last_month_multi = multi_seller_orders.filter(
        order__paid_at__gte=last_month_start,
        order__paid_at__lt=last_month_end
    ).aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
    last_month_multi = last_month_multi * Decimal('0.98')
    
    last_month_earnings = last_month_single + last_month_multi
    
    # Calculate total earnings
    total_single = single_seller_orders.aggregate(total=Sum('seller_amount'))['total'] or Decimal('0.00')
    total_multi = multi_seller_orders.aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
    total_multi = total_multi * Decimal('0.98')
    total_earnings = total_single + total_multi
    
    # Calculate pending payouts (paid but not yet delivered)
    pending_single = single_seller_orders.filter(
        status__in=['paid', 'shipped']
    ).aggregate(total=Sum('seller_amount'))['total'] or Decimal('0.00')
    
    pending_multi = multi_seller_orders.filter(
        order__status__in=['paid', 'shipped']
    ).aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
    pending_multi = pending_multi * Decimal('0.98')
    
    pending_payouts = pending_single + pending_multi
    
    # Earnings by month (last 12 months)
    earnings_by_month = []
    for i in range(11, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        month_single = single_seller_orders.filter(
            paid_at__gte=month_start,
            paid_at__lt=month_end
        ).aggregate(total=Sum('seller_amount'))['total'] or Decimal('0.00')
        
        month_multi = multi_seller_orders.filter(
            order__paid_at__gte=month_start,
            order__paid_at__lt=month_end
        ).aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
        month_multi = month_multi * Decimal('0.98')
        
        earnings_by_month.append({
            'month': month_start.strftime('%b %Y'),
            'amount': str(month_single + month_multi),
            'earnings': float(month_single + month_multi)
        })
    
    # Earnings by week (last 4 weeks)
    earnings_by_week = []
    for i in range(3, -1, -1):
        week_start = now - timedelta(days=7*(i+1))
        week_end = now - timedelta(days=7*i)
        
        week_single = single_seller_orders.filter(
            paid_at__gte=week_start,
            paid_at__lt=week_end
        ).aggregate(total=Sum('seller_amount'))['total'] or Decimal('0.00')
        
        week_multi = multi_seller_orders.filter(
            order__paid_at__gte=week_start,
            order__paid_at__lt=week_end
        ).aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
        week_multi = week_multi * Decimal('0.98')
        
        earnings_by_week.append({
            'name': f'Week {4-i}',
            'amount': str(week_single + week_multi),
            'earnings': float(week_single + week_multi)
        })
    
    # Earnings by quarter (last 4 quarters)
    earnings_by_quarter = []
    for i in range(3, -1, -1):
        quarter_start = now - timedelta(days=90*(i+1))
        quarter_end = now - timedelta(days=90*i)
        
        quarter_single = single_seller_orders.filter(
            paid_at__gte=quarter_start,
            paid_at__lt=quarter_end
        ).aggregate(total=Sum('seller_amount'))['total'] or Decimal('0.00')
        
        quarter_multi = multi_seller_orders.filter(
            order__paid_at__gte=quarter_start,
            order__paid_at__lt=quarter_end
        ).aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
        quarter_multi = quarter_multi * Decimal('0.98')
        
        earnings_by_quarter.append({
            'name': quarter_start.strftime('%b'),
            'amount': str(quarter_single + quarter_multi),
            'earnings': float(quarter_single + quarter_multi)
        })
    
    # Earnings by year (last 5 years)
    earnings_by_year = []
    for i in range(4, -1, -1):
        year_start = now.replace(month=1, day=1) - timedelta(days=365*i)
        year_end = year_start.replace(year=year_start.year + 1)
        
        year_single = single_seller_orders.filter(
            paid_at__gte=year_start,
            paid_at__lt=year_end
        ).aggregate(total=Sum('seller_amount'))['total'] or Decimal('0.00')
        
        year_multi = multi_seller_orders.filter(
            order__paid_at__gte=year_start,
            order__paid_at__lt=year_end
        ).aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
        year_multi = year_multi * Decimal('0.98')
        
        earnings_by_year.append({
            'name': str(year_start.year),
            'amount': str(year_single + year_multi),
            'earnings': float(year_single + year_multi)
        })
    
    return Response({
        'current_month': str(current_month_earnings),
        'last_month': str(last_month_earnings),
        'total_earnings': str(total_earnings),
        'pending_payouts': str(pending_payouts),
        'earnings_by_month': earnings_by_month,
        'earnings_by_week': earnings_by_week,
        'earnings_by_quarter': earnings_by_quarter,
        'earnings_by_year': earnings_by_year,
    })


# Seller Transactions Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_transactions(request):
    """Get seller transaction history"""
    from django.db.models import Q
    
    user = request.user
    
    # Check if user is a seller
    if user.role not in ['seller', 'both']:
        return Response(
            {'error': 'Only sellers can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get pagination parameters
    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))
    
    transactions = []
    
    # Get single-seller orders
    single_orders = Order.objects.filter(
        seller=user
    ).select_related('product').order_by('-created_at')
    
    for order in single_orders:
        # Determine status color
        if order.status in ['paid', 'shipped']:
            status_color = 'bg-amber-100 text-amber-700'
            transaction_status = 'Pending'
        elif order.status == 'delivered':
            status_color = 'bg-emerald-100 text-emerald-700'
            transaction_status = 'Completed'
        elif order.status == 'cancelled':
            status_color = 'bg-red-100 text-red-700'
            transaction_status = 'Cancelled'
        else:
            status_color = 'bg-gray-100 text-gray-700'
            transaction_status = order.status.replace('_', ' ').title()
        
        # Calculate amount
        amount = order.seller_amount if order.seller_amount else Decimal('0.00')
        
        transactions.append({
            'id': f'TXN-{order.order_number}',
            'description': f'Order {order.order_number} - {order.product.name if order.product else "Multiple Items"}',
            'date': order.paid_at if order.paid_at else order.created_at,
            'amount': f'+{amount:,.0f}',
            'status': transaction_status,
            'status_color': status_color,
            'order_id': order.id,
        })
    
    # Get multi-seller order items
    order_items = OrderItem.objects.filter(
        product__seller=user
    ).select_related('order', 'product').order_by('-order__created_at')
    
    for item in order_items:
        order = item.order
        
        # Determine status color
        if order.status in ['paid', 'shipped']:
            status_color = 'bg-amber-100 text-amber-700'
            transaction_status = 'Pending'
        elif order.status == 'delivered':
            status_color = 'bg-emerald-100 text-emerald-700'
            transaction_status = 'Completed'
        elif order.status == 'cancelled':
            status_color = 'bg-red-100 text-red-700'
            transaction_status = 'Cancelled'
        else:
            status_color = 'bg-gray-100 text-gray-700'
            transaction_status = order.status.replace('_', ' ').title()
        
        # Calculate amount (subtotal minus platform fee)
        amount = item.subtotal * Decimal('0.98')
        
        transactions.append({
            'id': f'TXN-{order.order_number}-{item.id}',
            'description': f'Order {order.order_number} - {item.product.name}',
            'date': order.paid_at if order.paid_at else order.created_at,
            'amount': f'+{amount:,.0f}',
            'status': transaction_status,
            'status_color': status_color,
            'order_id': order.id,
        })
    
    # Sort by date (newest first)
    transactions.sort(key=lambda x: x['date'], reverse=True)
    
    # Format dates
    for transaction in transactions:
        transaction['date'] = transaction['date'].strftime('%b %d, %Y')
    
    # Apply pagination
    total = len(transactions)
    transactions = transactions[offset:offset+limit]
    
    return Response({
        'transactions': transactions,
        'total': total,
        'limit': limit,
        'offset': offset,
    })


# Product Performance Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_performance(request):
    """Get product performance statistics"""
    from django.db.models import Count, Sum
    
    user = request.user
    
    # Check if user is a seller
    if user.role not in ['seller', 'both']:
        return Response(
            {'error': 'Only sellers can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get top products by sales (from delivered orders)
    # Single-seller orders
    single_sales = Order.objects.filter(
        seller=user,
        status='delivered',
        product__isnull=False
    ).values('product', 'product__name').annotate(
        sales_count=Count('id'),
        revenue=Sum('seller_amount')
    )
    
    # Multi-seller orders
    multi_sales = OrderItem.objects.filter(
        product__seller=user,
        order__status='delivered'
    ).values('product', 'product__name').annotate(
        sales_count=Count('id'),
        revenue=Sum('subtotal')
    )
    
    # Combine and aggregate
    product_stats = {}
    
    for sale in single_sales:
        product_id = sale['product']
        product_name = sale['product__name']
        if product_id not in product_stats:
            product_stats[product_id] = {
                'name': product_name,
                'sales': 0,
                'revenue': Decimal('0.00')
            }
        product_stats[product_id]['sales'] += sale['sales_count']
        product_stats[product_id]['revenue'] += sale['revenue'] or Decimal('0.00')
    
    for sale in multi_sales:
        product_id = sale['product']
        product_name = sale['product__name']
        if product_id not in product_stats:
            product_stats[product_id] = {
                'name': product_name,
                'sales': 0,
                'revenue': Decimal('0.00')
            }
        product_stats[product_id]['sales'] += sale['sales_count']
        # Apply platform fee reduction
        product_stats[product_id]['revenue'] += (sale['revenue'] or Decimal('0.00')) * Decimal('0.98')
    
    # Convert to list and sort by sales
    performance = list(product_stats.values())
    performance.sort(key=lambda x: x['sales'], reverse=True)
    
    # Get top 10 products
    performance = performance[:10]
    
    # Convert revenue to string
    for item in performance:
        item['revenue'] = str(item['revenue'])
    
    return Response({
        'products': performance
    })
