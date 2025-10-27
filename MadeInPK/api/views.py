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
import uuid

from .models import (
    Province, City, Address, Category, Product, ProductImage,
    AuctionListing, Bid, FixedPriceListing, Order, Payment,
    Feedback, Conversation, Message, Notification, Complaint, Wishlist, SellerProfile, ProductReview
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
    SellerProfileSerializer, ProductReviewSerializer, ProductReviewCreateSerializer
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
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get current user profile"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


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
        else:
            # By default, show only active auctions
            queryset = queryset.filter(status='active')
        
        # Filter by seller
        seller_id = self.request.query_params.get('seller')
        if seller_id:
            queryset = queryset.filter(product__seller_id=seller_id)
        
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
        else:
            # By default, show only active listings
            queryset = queryset.filter(status='active')
        
        # Filter by seller
        seller_id = self.request.query_params.get('seller')
        if seller_id:
            queryset = queryset.filter(product__seller_id=seller_id)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(product__category_id=category_id)
        
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
        
        # Create order
        total_amount = listing.price * quantity
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
            unit_price=listing.price,
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
        
        # Users can see orders where they are buyer or seller
        queryset = Order.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related(
            'buyer', 'seller', 'product', 'shipping_address__city__province'
        )
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by role (purchases or sales)
        role = self.request.query_params.get('role')
        if role == 'buyer':
            queryset = queryset.filter(buyer=user)
        elif role == 'seller':
            queryset = queryset.filter(seller=user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_shipped(self, request, pk=None):
        """Mark order as shipped (seller only)"""
        order = self.get_object()
        
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
        
        # Notify seller
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
        ).select_related('buyer', 'seller', 'order').prefetch_related('messages')
    
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
