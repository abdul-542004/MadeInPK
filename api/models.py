from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


# Custom User Model
class User(AbstractUser):
    """Extended user model with additional fields for buyers and sellers"""
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('both', 'Both'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    is_blocked = models.BooleanField(default=False)  # For blocking non-paying bidders
    failed_payment_count = models.IntegerField(default=0)  # Track failed payments
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)  # For sellers (Stripe Connect)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username


# Seller Profile Model
class SellerProfile(models.Model):
    """Extended profile for sellers with business information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    brand_name = models.CharField(max_length=255, blank=True)
    biography = models.TextField(blank=True)
    business_address_text = models.TextField(blank=True)  # Legacy text field (deprecated)
    business_address_id = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True, related_name='seller_profiles')  # New structured address
    business_phone = models.CharField(max_length=15, blank=True)  # Business contact number
    website = models.URLField(blank=True)
    social_media_links = models.JSONField(default=dict, blank=True)  # {'facebook': 'url', 'instagram': 'url'}
    is_verified = models.BooleanField(default=False)  # Admin verification
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_feedbacks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'seller_profiles'
    
    def __str__(self):
        return f"Seller Profile: {self.user.username} - {self.brand_name or 'No Brand'}"
    
    def get_province(self):
        """Get the province for this seller's business"""
        if self.business_address_id:
            return self.business_address_id.city.province
        # Fallback to user's default address
        default_address = self.user.addresses.filter(is_default=True).first()
        if default_address:
            return default_address.city.province
        return None
    
    def update_rating(self):
        """Update average rating from feedbacks"""
        feedbacks = Feedback.objects.filter(seller=self.user)
        if feedbacks.exists():
            avg_rating = feedbacks.aggregate(models.Avg('seller_rating'))['seller_rating__avg']
            self.average_rating = round(avg_rating, 2)
            self.total_feedbacks = feedbacks.count()
        else:
            self.average_rating = 0.00
            self.total_feedbacks = 0
        self.save()


# Address Models (Normalized)
class Province(models.Model):
    """Province/State information"""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'provinces'
    
    def __str__(self):
        return self.name


class City(models.Model):
    """City information linked to province"""
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')
    
    class Meta:
        db_table = 'cities'
        unique_together = ['name', 'province']
    
    def __str__(self):
        return f"{self.name}, {self.province.name}"


class Address(models.Model):
    """User address for shipping"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street_address = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='addresses')
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'addresses'
        verbose_name_plural = 'Addresses'
    
    def __str__(self):
        return f"{self.street_address}, {self.city}"


# Product Category
class Category(models.Model):
    """Product categories for organization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


# Product Model
class Product(models.Model):
    """Base product information - can be used in auction or fixed price listing"""
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    condition = models.CharField(max_length=50, choices=[
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
    
    def __str__(self):
        return self.name
    
    def get_region(self):
        """Get the region (province) this product belongs to based on seller's default address"""
        default_address = self.seller.addresses.filter(is_default=True).first()
        if default_address:
            return default_address.city.province
        # If no default address, get any address
        any_address = self.seller.addresses.first()
        if any_address:
            return any_address.city.province
        return None


class ProductImage(models.Model):
    """Product images - stored locally on server"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', max_length=500, null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0) # for ordering multiple images
    
    class Meta:
        db_table = 'product_images'
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.product.name}"


# Auction Listing
class AuctionListing(models.Model):
    """Auction listing for a single unique product"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('ended', 'Ended'), # Auction ended, winner not determined
        ('cancelled', 'Cancelled'),  # Auction cancelled, winner refused to pay
        ('completed', 'Completed'),  # Payment successful
    ]
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='auction')
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_auctions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auction_listings'
    
    def __str__(self):
        return f"Auction: {self.product.name}"
    
    def is_active(self):
        now = timezone.now()
        return self.status == 'active' and self.start_time <= now <= self.end_time


# Bid Model
class Bid(models.Model):
    """Bids placed on auction listings"""
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    bid_time = models.DateTimeField(auto_now_add=True)
    is_winning = models.BooleanField(default=False)  # Current winning bid
    
    class Meta:
        db_table = 'bids'
        ordering = ['-bid_time']
        indexes = [
            models.Index(fields=['auction', '-amount']),
        ]
    
    def __str__(self):
        return f"Bid by {self.bidder.username} on {self.auction.product.name}: ${self.amount}"


# Fixed Price Listing
class FixedPriceListing(models.Model):
    """Fixed price listing for products (can have quantity)"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='fixed_price')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    featured = models.BooleanField(default=False)
    
    # Discount fields
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('99.99'))]
    )
    discount_start_date = models.DateTimeField(null=True, blank=True)
    discount_end_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fixed_price_listings'
    
    def __str__(self):
        return f"Fixed Price: {self.product.name} - ${self.price}"
    
    def get_current_price(self):
        """Get the current price considering active discount"""
        if self.has_active_discount():
            discount_amount = self.price * (self.discount_percentage / Decimal('100'))
            return self.price - discount_amount
        return self.price
    
    def has_active_discount(self):
        """Check if the listing has an active discount"""
        if not self.discount_percentage or not self.discount_start_date or not self.discount_end_date:
            return False
        
        now = timezone.now()
        return self.discount_start_date <= now <= self.discount_end_date
    
    def reduce_quantity(self, amount):
        """Reduce quantity and update status if out of stock"""
        self.quantity -= amount
        if self.quantity <= 0:
            self.status = 'out_of_stock'
        self.save()


# Order Model
class Order(models.Model):
    """Order created after successful purchase"""
    ORDER_TYPE_CHOICES = [
        ('auction', 'Auction'),
        ('fixed_price', 'Fixed Price'),
        ('cart', 'Cart Checkout'),  # Multi-product order from cart
    ]
    
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('payment_failed', 'Payment Failed'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    
    # For single-product orders (auction or direct fixed-price purchase)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders', null=True, blank=True)
    auction = models.ForeignKey(AuctionListing, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    fixed_price_listing = models.ForeignKey(FixedPriceListing, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    quantity = models.IntegerField(default=1, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Total order amounts
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)  # 2% commission
    seller_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # For single seller orders
    
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    
    # Stripe payment fields
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    payment_url = models.URLField(max_length=500, blank=True)
    payment_deadline = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.buyer.username}"
    
    def calculate_amounts(self):
        """Calculate platform fee and seller amount"""
        self.platform_fee = self.total_amount * Decimal('0.02')
        if self.order_type in ['auction', 'fixed_price']:
            # Single seller order
            self.seller_amount = self.total_amount - self.platform_fee
    
    def is_multi_seller(self):
        """Check if this is a multi-seller order (cart checkout)"""
        return self.order_type == 'cart'
    
    def get_sellers(self):
        """Get all sellers involved in this order"""
        if self.is_multi_seller():
            return User.objects.filter(
                products__order_items__order=self
            ).distinct()
        elif self.seller:
            return [self.seller]
        return []


# Payment Model
class Payment(models.Model):
    """Payment transactions via Stripe"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
    
    def __str__(self):
        return f"Payment for Order {self.order.order_number}: {self.status}"


# Seller Transfer Model (for tracking transfers to sellers in Stripe Connect)
class SellerTransfer(models.Model):
    """Track individual transfers to sellers for multi-seller orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='seller_transfers')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transfers')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_transfer_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'seller_transfers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transfer to {self.seller.username}: ${self.amount} ({self.status})"


# Feedback Model
class Feedback(models.Model):
    """Feedback for seller and platform after successful purchase"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='feedback')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks_given')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks_received')
    
    # Seller rating
    seller_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    seller_comment = models.TextField(blank=True)
    
    # Platform rating
    platform_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    platform_comment = models.TextField(blank=True)
    
    # Specific aspects
    communication_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    product_as_described = models.BooleanField(default=True)
    shipping_speed_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feedbacks'
    
    def __str__(self):
        return f"Feedback by {self.buyer.username} for Order {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update seller's average rating
        if hasattr(self.seller, 'seller_profile'):
            self.seller.seller_profile.update_rating()


# Message Model (for buyer-seller communication)
class Conversation(models.Model):
    """Conversation between buyer and seller about a specific product"""
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_buyer')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_seller')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversations'
        unique_together = ['buyer', 'seller', 'product']
    
    def __str__(self):
        product_name = self.product.name if self.product else 'General Inquiry'
        return f"Conversation: {self.buyer.username} - {self.seller.username} about {product_name}"


class Message(models.Model):
    """Messages within a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"


# Notification Model
class Notification(models.Model):
    """Notifications for users (sent via email/SMTP)"""
    TYPE_CHOICES = [
        ('bid_placed', 'Bid Placed'),
        ('bid_outbid', 'Bid Outbid'),
        ('auction_won', 'Auction Won'),
        ('auction_lost', 'Auction Lost'),
        ('auction_ended', 'Auction Ended'),
        ('payment_reminder', 'Payment Reminder'),
        ('payment_received', 'Payment Received'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('feedback_request', 'Feedback Request'),
        ('message_received', 'Message Received'),
        ('account_blocked', 'Account Blocked'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_sent_via_email = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Optional references
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


# Complaint Model
class Complaint(models.Model):
    """User complaints about platform, sellers, or issues"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('payment', 'Payment Issue'),
        ('seller', 'Seller Issue'),
        ('product', 'Product Issue'),
        ('platform', 'Platform Issue'),
        ('shipping', 'Shipping Issue'),
        ('other', 'Other'),
    ]
    
    complaint_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    
    # Optional references
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints_against')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'complaints'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Complaint {self.complaint_number}: {self.subject}"


# Non-Paying User Tracker
class PaymentViolation(models.Model):
    """Track users who win auctions but fail to pay"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_violations')
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='payment_violations')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_violations')
    violation_date = models.DateTimeField(auto_now_add=True)
    payment_deadline = models.DateTimeField()
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payment_violations'
        ordering = ['-violation_date']
    
    def __str__(self):
        return f"Payment Violation by {self.user.username} - Order {self.order.order_number}"


# Wishlist Model
class Wishlist(models.Model):
    """User wishlists for saving products they're interested in"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_entries')
    notes = models.TextField(blank=True)  # Optional personal notes
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wishlists'
        unique_together = ['user', 'product']  # Prevent duplicate wishlist entries
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Wishlist: {self.user.username} - {self.product.name}"


# Product Review Model (for fixed-price products only)
class ProductReview(models.Model):
    """Reviews for fixed-price products (not for auctions)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='product_review', null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)  # True if linked to an order
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_reviews'
        ordering = ['-created_at']
        # One review per user per product
        unique_together = ['product', 'buyer']
    
    def __str__(self):
        return f"Review by {self.buyer.username} for {self.product.name}: {self.rating}/5"
    
    def save(self, *args, **kwargs):
        # Ensure only fixed-price products can be reviewed
        if hasattr(self.product, 'auction'):
            raise ValueError("Auction products cannot be reviewed")
        super().save(*args, **kwargs)


# Shopping Cart Model
class Cart(models.Model):
    """Shopping cart for buyers to add multiple fixed-price products"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def get_total_price(self):
        """Get total price of all items in cart"""
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.get_subtotal()
        return total
    
    def get_sellers(self):
        """Get unique list of sellers in this cart"""
        return User.objects.filter(
            products__fixed_price__cart_items__cart=self
        ).distinct()


class CartItem(models.Model):
    """Individual item in a shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    listing = models.ForeignKey(FixedPriceListing, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'listing']  # One listing per cart
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.quantity}x {self.listing.product.name} in {self.cart.user.username}'s cart"
    
    def get_subtotal(self):
        """Get subtotal for this cart item (quantity * current price with discount)"""
        return self.listing.get_current_price() * self.quantity
    
    def is_available(self):
        """Check if the item is still available in requested quantity"""
        return (
            self.listing.status == 'active' and
            self.listing.quantity >= self.quantity
        )


# Order Item Model (for orders with multiple products)
class OrderItem(models.Model):
    """Individual item within an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    listing = models.ForeignKey(FixedPriceListing, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of purchase
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # quantity * unit_price
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate subtotal
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)