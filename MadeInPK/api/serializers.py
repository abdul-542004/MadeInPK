from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Province, City, Address, Category, Product, ProductImage,
    AuctionListing, Bid, FixedPriceListing, Order, Payment,
    Feedback, Conversation, Message, Notification, Complaint
)

User = get_user_model()


# User Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'phone_number', 'role']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'phone_number', 'role', 'is_blocked', 'failed_payment_count', 
                  'created_at']
        read_only_fields = ['is_blocked', 'failed_payment_count']


class UserProfileSerializer(serializers.ModelSerializer):
    total_sales = serializers.SerializerMethodField()
    total_purchases = serializers.SerializerMethodField()
    average_seller_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'phone_number', 'role', 'created_at', 'total_sales', 
                  'total_purchases', 'average_seller_rating']
    
    def get_total_sales(self, obj):
        return obj.sales.filter(status='delivered').count()
    
    def get_total_purchases(self, obj):
        return obj.purchases.filter(status='delivered').count()
    
    def get_average_seller_rating(self, obj):
        feedbacks = obj.feedbacks_received.all()
        if feedbacks.exists():
            return sum(f.seller_rating for f in feedbacks) / feedbacks.count()
        return None


# Address Serializers
class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name']


class CitySerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source='province.name', read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'province', 'province_name']


class AddressSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    province_name = serializers.CharField(source='city.province.name', read_only=True)
    
    class Meta:
        model = Address
        fields = ['id', 'street_address', 'city', 'city_name', 'province_name', 
                  'postal_code', 'is_default', 'created_at']
        read_only_fields = ['created_at']


# Category Serializers
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'subcategories']
    
    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []


# Product Serializers
class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'is_primary', 'order']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    listing_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'seller', 'seller_username', 'category', 'category_name',
                  'name', 'description', 'condition', 'images', 'listing_type',
                  'created_at', 'updated_at']
        read_only_fields = ['seller', 'created_at', 'updated_at']
    
    def get_listing_type(self, obj):
        if hasattr(obj, 'auction'):
            return 'auction'
        elif hasattr(obj, 'fixed_price'):
            return 'fixed_price'
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), 
        write_only=True, 
        required=False
    )
    
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'condition', 'images']
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        
        # Create product images
        for idx, image_file in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image=image_file,
                is_primary=(idx == 0),
                order=idx
            )
        
        return product


# Auction Serializers
class BidSerializer(serializers.ModelSerializer):
    bidder_username = serializers.CharField(source='bidder.username', read_only=True)
    
    class Meta:
        model = Bid
        fields = ['id', 'bidder', 'bidder_username', 'amount', 'bid_time', 'is_winning']
        read_only_fields = ['bidder', 'bid_time', 'is_winning']


class AuctionListingSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    winner_username = serializers.CharField(source='winner.username', read_only=True)
    latest_bids = serializers.SerializerMethodField()
    total_bids = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = AuctionListing
        fields = ['id', 'product', 'starting_price', 'reserve_price', 'current_price',
                  'start_time', 'end_time', 'status', 'winner', 'winner_username',
                  'latest_bids', 'total_bids', 'time_remaining', 'created_at']
        read_only_fields = ['current_price', 'status', 'winner', 'created_at']
    
    def get_latest_bids(self, obj):
        bids = obj.bids.select_related('bidder').order_by('-bid_time')[:5]
        return BidSerializer(bids, many=True).data
    
    def get_total_bids(self, obj):
        return obj.bids.count()
    
    def get_time_remaining(self, obj):
        if obj.is_active():
            from django.utils import timezone
            remaining = obj.end_time - timezone.now()
            return remaining.total_seconds()
        return 0


class AuctionCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = AuctionListing
        fields = ['product_id', 'starting_price', 'reserve_price', 'start_time', 'end_time']
    
    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            # Check if product already has a listing
            if hasattr(product, 'auction') or hasattr(product, 'fixed_price'):
                raise serializers.ValidationError("Product already has a listing")
            # Check if user is the seller
            if product.seller != self.context['request'].user:
                raise serializers.ValidationError("You can only create auctions for your own products")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
    
    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time")
        if data.get('reserve_price') and data['reserve_price'] < data['starting_price']:
            raise serializers.ValidationError("Reserve price cannot be less than starting price")
        return data
    
    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)
        
        auction = AuctionListing.objects.create(
            product=product,
            current_price=validated_data['starting_price'],
            **validated_data
        )
        return auction


class BidCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['amount']
    
    def validate_amount(self, value):
        auction = self.context['auction']
        if value <= auction.current_price:
            raise serializers.ValidationError(
                f"Bid must be higher than current price of {auction.current_price}"
            )
        return value
    
    def create(self, validated_data):
        auction = self.context['auction']
        user = self.context['request'].user
        
        # Mark previous winning bids as not winning
        Bid.objects.filter(auction=auction, is_winning=True).update(is_winning=False)
        
        # Create new bid
        bid = Bid.objects.create(
            auction=auction,
            bidder=user,
            is_winning=True,
            **validated_data
        )
        
        # Update auction current price
        auction.current_price = bid.amount
        auction.save()
        
        return bid


# Fixed Price Listing Serializers
class FixedPriceListingSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = FixedPriceListing
        fields = ['id', 'product', 'price', 'quantity', 'status', 'created_at', 'updated_at']
        read_only_fields = ['status', 'created_at', 'updated_at']


class FixedPriceCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FixedPriceListing
        fields = ['product_id', 'price', 'quantity']
    
    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            if hasattr(product, 'auction') or hasattr(product, 'fixed_price'):
                raise serializers.ValidationError("Product already has a listing")
            if product.seller != self.context['request'].user:
                raise serializers.ValidationError("You can only create listings for your own products")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
    
    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)
        
        listing = FixedPriceListing.objects.create(
            product=product,
            **validated_data
        )
        return listing


# Order Serializers
class OrderSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    shipping_address_detail = AddressSerializer(source='shipping_address', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'buyer', 'buyer_username', 'seller', 
                  'seller_username', 'product', 'product_name', 'order_type',
                  'quantity', 'unit_price', 'total_amount', 'platform_fee',
                  'seller_amount', 'shipping_address', 'shipping_address_detail',
                  'status', 'payment_url', 'payment_deadline', 'created_at',
                  'paid_at', 'shipped_at', 'delivered_at']
        read_only_fields = ['order_number', 'buyer', 'seller', 'platform_fee',
                           'seller_amount', 'status', 'created_at', 'paid_at',
                           'shipped_at', 'delivered_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    listing_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(default=1)
    
    class Meta:
        model = Order
        fields = ['listing_id', 'quantity', 'shipping_address']
    
    def validate(self, data):
        listing_id = data['listing_id']
        quantity = data['quantity']
        
        try:
            listing = FixedPriceListing.objects.select_related('product').get(id=listing_id)
            
            if listing.status != 'active':
                raise serializers.ValidationError("Listing is not active")
            
            if listing.quantity < quantity:
                raise serializers.ValidationError("Not enough quantity available")
            
            data['listing'] = listing
            return data
            
        except FixedPriceListing.DoesNotExist:
            raise serializers.ValidationError("Listing not found")


# Payment Serializers
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'stripe_payment_intent_id', 'amount', 'status',
                  'payment_method', 'created_at', 'completed_at']
        read_only_fields = ['stripe_payment_intent_id', 'status', 'created_at', 'completed_at']


# Feedback Serializers
class FeedbackSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'order', 'order_number', 'buyer', 'buyer_username',
                  'seller_rating', 'seller_comment', 'platform_rating',
                  'platform_comment', 'communication_rating', 'product_as_described',
                  'shipping_speed_rating', 'created_at']
        read_only_fields = ['buyer', 'seller', 'created_at']


class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['seller_rating', 'seller_comment', 'platform_rating',
                  'platform_comment', 'communication_rating', 'product_as_described',
                  'shipping_speed_rating']


# Message Serializers
class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_username', 'content', 'is_read', 'created_at']
        read_only_fields = ['sender', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    latest_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'buyer', 'buyer_username', 'seller', 'seller_username',
                  'order', 'order_number', 'latest_message', 'unread_count',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_latest_message(self, obj):
        message = obj.messages.last()
        if message:
            return MessageSerializer(message).data
        return None
    
    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()


# Notification Serializers
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read',
                  'order', 'auction', 'created_at']
        read_only_fields = ['created_at']


# Complaint Serializers
class ComplaintSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Complaint
        fields = ['id', 'complaint_number', 'user', 'user_username', 'category',
                  'subject', 'description', 'order', 'order_number', 'seller',
                  'seller_username', 'status', 'created_at', 'updated_at']
        read_only_fields = ['complaint_number', 'user', 'status', 'created_at', 'updated_at']


class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['category', 'subject', 'description', 'order', 'seller']
    
    def create(self, validated_data):
        import uuid
        validated_data['complaint_number'] = f"CMP-{uuid.uuid4().hex[:12].upper()}"
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
