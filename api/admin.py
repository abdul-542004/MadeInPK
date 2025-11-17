from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path
from django.shortcuts import redirect
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from .models import (
    User, Province, City, Address, Category, Product, ProductImage,
    AuctionListing, Bid, FixedPriceListing, Order, Payment,
    Feedback, Conversation, Message, Notification, Complaint, PaymentViolation, SellerProfile, Wishlist, ProductReview,
    Cart, CartItem, OrderItem, SellerTransfer
)


# Custom Admin Site
class MadeInPKAdminSite(admin.AdminSite):
    site_header = "MadeInPK Administration"
    site_title = "MadeInPK Admin Portal"
    index_title = "Welcome to MadeInPK Administration"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='admin_dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        from .admin_dashboard import admin_dashboard
        return admin_dashboard(request)
    
    def index(self, request, extra_context=None):
        # Redirect to custom dashboard instead of default admin index
        return redirect('admin:admin_dashboard')


# Replace default admin site
admin_site = MadeInPKAdminSite(name='admin')
admin.site = admin_site
admin.sites.site = admin_site


@admin.register(User, site=admin_site)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_blocked', 'failed_payment_count', 'total_orders', 'total_spent', 'date_joined', 'last_login']
    list_filter = ['role', 'is_blocked', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ['date_joined', 'last_login', 'total_orders', 'total_spent', 'total_sales']
    actions = ['block_users', 'unblock_users', 'reset_failed_payments']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Contact Information', {
            'fields': ('phone_number', 'profile_picture')
        }),
        ('Role & Status', {
            'fields': ('role', 'is_blocked', 'failed_payment_count')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_customer_id', 'stripe_account_id'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_orders', 'total_spent', 'total_sales'),
            'classes': ('collapse',)
        }),
    )
    
    def total_orders(self, obj):
        """Total number of orders placed by this user"""
        count = obj.purchases.count()
        return f"{count} orders"
    total_orders.short_description = 'Total Orders'
    
    def total_spent(self, obj):
        """Total amount spent by this user"""
        total = obj.purchases.filter(
            status__in=['paid', 'shipped', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        return f"Rs {total:,.2f}"
    total_spent.short_description = 'Total Spent'
    
    def total_sales(self, obj):
        """Total sales if user is a seller"""
        if obj.role in ['seller', 'both']:
            total = obj.sales.filter(
                status__in=['paid', 'shipped', 'delivered']
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            return f"Rs {total:,.2f}"
        return "N/A"
    total_sales.short_description = 'Total Sales'
    
    def block_users(self, request, queryset):
        """Block selected users"""
        updated = queryset.update(is_blocked=True)
        self.message_user(request, f'{updated} user(s) blocked successfully.')
    block_users.short_description = 'Block selected users'
    
    def unblock_users(self, request, queryset):
        """Unblock selected users"""
        updated = queryset.update(is_blocked=False)
        self.message_user(request, f'{updated} user(s) unblocked successfully.')
    unblock_users.short_description = 'Unblock selected users'
    
    def reset_failed_payments(self, request, queryset):
        """Reset failed payment count"""
        updated = queryset.update(failed_payment_count=0)
        self.message_user(request, f'Failed payment count reset for {updated} user(s).')
    reset_failed_payments.short_description = 'Reset failed payment count'


@admin.register(Province, site=admin_site)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'city_count']
    search_fields = ['name']
    
    def city_count(self, obj):
        """Number of cities in this province"""
        return obj.cities.count()
    city_count.short_description = 'Cities'


@admin.register(City, site=admin_site)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'province']
    list_filter = ['province']
    search_fields = ['name']


@admin.register(Address, site=admin_site)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'street_address', 'city', 'postal_code', 'is_default', 'created_at']
    list_filter = ['is_default', 'city__province', 'created_at']
    search_fields = ['user__username', 'street_address', 'city__name']
    autocomplete_fields = ['user', 'city']
    actions = ['set_as_default']
    
    def set_as_default(self, request, queryset):
        """Set selected addresses as default for their users"""
        for address in queryset:
            # Remove default from other addresses of same user
            Address.objects.filter(user=address.user).update(is_default=False)
            address.is_default = True
            address.save()
        self.message_user(request, f'{queryset.count()} address(es) set as default.')
    set_as_default.short_description = 'Set as default address'


@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'product_count', 'has_subcategories']
    search_fields = ['name', 'description']
    list_filter = ['parent']
    
    def product_count(self, obj):
        """Number of products in this category"""
        return obj.products.count()
    product_count.short_description = 'Products'
    
    def has_subcategories(self, obj):
        """Check if category has subcategories"""
        return obj.subcategories.exists()
    has_subcategories.boolean = True
    has_subcategories.short_description = 'Has Subcategories'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product, site=admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'seller', 'category', 'condition', 'listing_type', 'price_display', 'status_display', 'created_at']
    list_filter = ['condition', 'category', 'created_at', 'seller__role']
    search_fields = ['name', 'description', 'seller__username']
    autocomplete_fields = ['seller', 'category']
    inlines = [ProductImageInline]
    readonly_fields = ['created_at', 'updated_at', 'total_views', 'total_sales']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'seller', 'category', 'condition')
        }),
        ('Statistics', {
            'fields': ('total_views', 'total_sales'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def listing_type(self, obj):
        """Display listing type"""
        if hasattr(obj, 'auction'):
            return '🔨 Auction'
        elif hasattr(obj, 'fixed_price'):
            return '💰 Fixed Price'
        return '❓ No Listing'
    listing_type.short_description = 'Type'
    
    def price_display(self, obj):
        """Display price based on listing type"""
        if hasattr(obj, 'auction'):
            return f"Rs {obj.auction.current_price:,.2f}"
        elif hasattr(obj, 'fixed_price'):
            return f"Rs {obj.fixed_price.price:,.2f}"
        return "N/A"
    price_display.short_description = 'Price'
    
    def status_display(self, obj):
        """Display status based on listing type"""
        if hasattr(obj, 'auction'):
            return obj.auction.get_status_display()
        elif hasattr(obj, 'fixed_price'):
            return obj.fixed_price.get_status_display()
        return "No Listing"
    status_display.short_description = 'Status'
    
    def total_views(self, obj):
        """Total views (placeholder - can be implemented later)"""
        return "N/A"
    total_views.short_description = 'Views'
    
    def total_sales(self, obj):
        """Total number of times this product was sold"""
        count = obj.orders.filter(status__in=['paid', 'shipped', 'delivered']).count()
        count += obj.order_items.filter(order__status__in=['paid', 'shipped', 'delivered']).count()
        return count
    total_sales.short_description = 'Sales'


@admin.register(AuctionListing, site=admin_site)
class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'starting_price', 'current_price', 'bid_count', 'status', 
                    'time_remaining', 'winner', 'created_at']
    list_filter = ['status', 'start_time', 'end_time', 'created_at']
    search_fields = ['product__name', 'winner__username', 'product__seller__username']
    readonly_fields = ['current_price', 'winner', 'created_at', 'updated_at', 'bid_count', 'time_remaining']
    autocomplete_fields = ['product']
    actions = ['end_auction', 'cancel_auction']
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Auction Details', {
            'fields': ('product', 'starting_price', 'current_price')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'time_remaining')
        }),
        ('Status', {
            'fields': ('status', 'winner')
        }),
        ('Statistics', {
            'fields': ('bid_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def bid_count(self, obj):
        """Number of bids placed"""
        return obj.bids.count()
    bid_count.short_description = 'Bids'
    
    def time_remaining(self, obj):
        """Time remaining in auction"""
        if obj.status != 'active':
            return "N/A"
        now = timezone.now()
        if now > obj.end_time:
            return "Ended"
        elif now < obj.start_time:
            delta = obj.start_time - now
            return f"Starts in {delta.days}d {delta.seconds//3600}h"
        else:
            delta = obj.end_time - now
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            return f"{delta.days}d {hours}h {minutes}m"
    time_remaining.short_description = 'Time Remaining'
    
    def end_auction(self, request, queryset):
        """End selected auctions"""
        updated = queryset.filter(status='active').update(status='ended')
        self.message_user(request, f'{updated} auction(s) ended.')
    end_auction.short_description = 'End selected auctions'
    
    def cancel_auction(self, request, queryset):
        """Cancel selected auctions"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} auction(s) cancelled.')
    cancel_auction.short_description = 'Cancel selected auctions'


@admin.register(Bid, site=admin_site)
class BidAdmin(admin.ModelAdmin):
    list_display = ['id', 'auction_product', 'bidder', 'amount', 'bid_time', 'is_winning', 'bid_rank']
    list_filter = ['is_winning', 'bid_time']
    search_fields = ['auction__product__name', 'bidder__username']
    readonly_fields = ['bid_time', 'bid_rank']
    autocomplete_fields = ['auction', 'bidder']
    date_hierarchy = 'bid_time'
    
    def auction_product(self, obj):
        """Display auction product name"""
        return obj.auction.product.name
    auction_product.short_description = 'Product'
    
    def bid_rank(self, obj):
        """Rank of this bid in the auction"""
        higher_bids = obj.auction.bids.filter(amount__gt=obj.amount).count()
        return f"#{higher_bids + 1}"
    bid_rank.short_description = 'Rank'


@admin.register(FixedPriceListing, site=admin_site)
class FixedPriceListingAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'price', 'discounted_price', 'quantity', 'status', 'featured', 'created_at']
    list_filter = ['status', 'featured', 'created_at']
    search_fields = ['product__name', 'product__seller__username']
    autocomplete_fields = ['product']
    readonly_fields = ['created_at', 'updated_at', 'effective_price', 'total_revenue']
    actions = ['mark_featured', 'mark_not_featured', 'activate_listings', 'deactivate_listings']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Product & Pricing', {
            'fields': ('product', 'price', 'quantity', 'effective_price')
        }),
        ('Discount', {
            'fields': ('discount_percentage', 'discount_start_date', 'discount_end_date'),
            'classes': ('collapse',)
        }),
        ('Status & Features', {
            'fields': ('status', 'featured')
        }),
        ('Statistics', {
            'fields': ('total_revenue',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def discounted_price(self, obj):
        """Show discounted price if active"""
        if obj.has_active_discount():
            current = obj.get_current_price()
            return f"Rs {current:,.2f} ({obj.discount_percentage}% off)"
        return "N/A"
    discounted_price.short_description = 'Discounted Price'
    
    def effective_price(self, obj):
        """Current effective price"""
        return f"Rs {obj.get_current_price():,.2f}"
    effective_price.short_description = 'Current Price'
    
    def total_revenue(self, obj):
        """Total revenue from this listing"""
        revenue = obj.order_items.filter(
            order__status__in=['paid', 'shipped', 'delivered']
        ).aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
        return f"Rs {revenue:,.2f}"
    total_revenue.short_description = 'Total Revenue'
    
    def mark_featured(self, request, queryset):
        """Mark selected listings as featured"""
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} listing(s) marked as featured.')
    mark_featured.short_description = 'Mark as featured'
    
    def mark_not_featured(self, request, queryset):
        """Remove featured status"""
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} listing(s) unmarked as featured.')
    mark_not_featured.short_description = 'Remove featured status'
    
    def activate_listings(self, request, queryset):
        """Activate selected listings"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} listing(s) activated.')
    activate_listings.short_description = 'Activate selected listings'
    
    def deactivate_listings(self, request, queryset):
        """Deactivate selected listings"""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} listing(s) deactivated.')
    deactivate_listings.short_description = 'Deactivate selected listings'


@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'buyer', 'seller_display', 'order_type', 
                    'total_amount', 'platform_fee', 'status', 'payment_status', 'created_at']
    list_filter = ['order_type', 'status', 'created_at', 'paid_at']
    search_fields = ['order_number', 'buyer__username', 'seller__username', 'product__name']
    readonly_fields = ['order_number', 'platform_fee', 'seller_amount', 'created_at', 
                      'paid_at', 'shipped_at', 'delivered_at', 'payment_url', 'age']
    autocomplete_fields = ['buyer', 'seller', 'product', 'shipping_address']
    actions = ['mark_as_paid', 'mark_as_shipped', 'cancel_orders', 'export_to_csv']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'buyer', 'order_type', 'age')
        }),
        ('Product Details (Single Orders)', {
            'fields': ('seller', 'product', 'auction', 'fixed_price_listing', 'quantity', 'unit_price'),
            'classes': ('collapse',)
        }),
        ('Amounts', {
            'fields': ('total_amount', 'platform_fee', 'seller_amount')
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
        ('Payment', {
            'fields': ('status', 'stripe_payment_intent_id', 'payment_url', 'payment_deadline'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'paid_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def seller_display(self, obj):
        """Display seller or multi-seller indicator"""
        if obj.is_multi_seller():
            sellers = obj.get_sellers()
            return f"Multi-seller ({len(sellers)})"
        return obj.seller.username if obj.seller else "N/A"
    seller_display.short_description = 'Seller'
    
    def payment_status(self, obj):
        """Display payment status with color"""
        if obj.status in ['paid', 'shipped', 'delivered']:
            return '✅ Paid'
        elif obj.status == 'pending_payment':
            return '⏳ Pending'
        elif obj.status == 'payment_failed':
            return '❌ Failed'
        return obj.get_status_display()
    payment_status.short_description = 'Payment'
    
    def age(self, obj):
        """Order age"""
        delta = timezone.now() - obj.created_at
        if delta.days > 0:
            return f"{delta.days} days ago"
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours} hours ago"
        minutes = (delta.seconds % 3600) // 60
        return f"{minutes} minutes ago"
    age.short_description = 'Age'
    
    def mark_as_paid(self, request, queryset):
        """Mark orders as paid"""
        updated = queryset.filter(status='pending_payment').update(
            status='paid',
            paid_at=timezone.now()
        )
        self.message_user(request, f'{updated} order(s) marked as paid.')
    mark_as_paid.short_description = 'Mark as paid'
    
    def mark_as_shipped(self, request, queryset):
        """Mark orders as shipped"""
        updated = queryset.filter(status='paid').update(
            status='shipped',
            shipped_at=timezone.now()
        )
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = 'Mark as shipped'
    
    def cancel_orders(self, request, queryset):
        """Cancel selected orders"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} order(s) cancelled.')
    cancel_orders.short_description = 'Cancel selected orders'
    
    def export_to_csv(self, request, queryset):
        """Export selected orders to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order Number', 'Buyer', 'Seller', 'Type', 'Amount', 'Status', 'Date'])
        
        for order in queryset:
            writer.writerow([
                order.order_number,
                order.buyer.username,
                order.seller.username if order.seller else 'Multi-seller',
                order.get_order_type_display(),
                order.total_amount,
                order.get_status_display(),
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    export_to_csv.short_description = 'Export to CSV'


@admin.register(Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'amount', 'status', 'payment_method', 'created_at', 'completed_at', 'duration']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order__order_number', 'stripe_payment_intent_id']
    readonly_fields = ['created_at', 'completed_at', 'updated_at', 'duration']
    autocomplete_fields = ['order']
    date_hierarchy = 'created_at'
    
    def order_number(self, obj):
        """Display order number"""
        return obj.order.order_number
    order_number.short_description = 'Order'
    
    def duration(self, obj):
        """Payment processing duration"""
        if obj.completed_at:
            delta = obj.completed_at - obj.created_at
            minutes = delta.seconds // 60
            seconds = delta.seconds % 60
            return f"{minutes}m {seconds}s"
        return "N/A"
    duration.short_description = 'Processing Time'


@admin.register(Feedback, site=admin_site)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'buyer', 'seller', 'seller_rating', 
                    'platform_rating', 'product_as_described', 'created_at']
    list_filter = ['seller_rating', 'platform_rating', 'product_as_described', 'created_at', 
                   'communication_rating', 'shipping_speed_rating']
    search_fields = ['buyer__username', 'seller__username', 'order__order_number', 
                     'seller_comment', 'platform_comment']
    readonly_fields = ['created_at', 'average_rating']
    autocomplete_fields = ['order', 'buyer', 'seller']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('order', 'buyer', 'seller', 'average_rating')
        }),
        ('Seller Feedback', {
            'fields': ('seller_rating', 'seller_comment', 'communication_rating', 
                      'shipping_speed_rating', 'product_as_described')
        }),
        ('Platform Feedback', {
            'fields': ('platform_rating', 'platform_comment')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def order_number(self, obj):
        """Display order number"""
        return obj.order.order_number
    order_number.short_description = 'Order'
    
    def average_rating(self, obj):
        """Average of all ratings"""
        avg = (obj.seller_rating + obj.communication_rating + obj.shipping_speed_rating) / 3
        return f"{avg:.2f} / 5.00"
    average_rating.short_description = 'Avg Rating'


@admin.register(Conversation, site=admin_site)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'seller', 'product', 'message_count', 'last_message_time', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['buyer__username', 'seller__username', 'product__name']
    readonly_fields = ['created_at', 'updated_at', 'message_count', 'last_message_time']
    autocomplete_fields = ['buyer', 'seller', 'product']
    
    def message_count(self, obj):
        """Number of messages in conversation"""
        return obj.messages.count()
    message_count.short_description = 'Messages'
    
    def last_message_time(self, obj):
        """Time of last message"""
        last_msg = obj.messages.last()
        if last_msg:
            return last_msg.created_at
        return "No messages"
    last_message_time.short_description = 'Last Message'


@admin.register(Message, site=admin_site)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation_info', 'sender', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'content', 'conversation__buyer__username', 
                     'conversation__seller__username']
    readonly_fields = ['created_at']
    autocomplete_fields = ['conversation', 'sender']
    actions = ['mark_as_read', 'mark_as_unread']
    date_hierarchy = 'created_at'
    
    def conversation_info(self, obj):
        """Display conversation participants"""
        return f"{obj.conversation.buyer.username} ↔ {obj.conversation.seller.username}"
    conversation_info.short_description = 'Conversation'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Message'
    
    def mark_as_read(self, request, queryset):
        """Mark messages as read"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read.short_description = 'Mark as read'
    
    def mark_as_unread(self, request, queryset):
        """Mark messages as unread"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')
    mark_as_unread.short_description = 'Mark as unread'


@admin.register(Notification, site=admin_site)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notification_type', 'title', 'is_read', 
                    'is_sent_via_email', 'email_status', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_sent_via_email', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'email_sent_at']
    autocomplete_fields = ['user', 'order', 'auction']
    actions = ['mark_as_read', 'send_email_notifications']
    date_hierarchy = 'created_at'
    
    def email_status(self, obj):
        """Email sent status with icon"""
        if obj.is_sent_via_email:
            return '✅ Sent'
        return '❌ Not Sent'
    email_status.short_description = 'Email'
    
    def mark_as_read(self, request, queryset):
        """Mark notifications as read"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notification(s) marked as read.')
    mark_as_read.short_description = 'Mark as read'
    
    def send_email_notifications(self, request, queryset):
        """Send email for selected notifications"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        count = 0
        for notification in queryset.filter(is_sent_via_email=False):
            try:
                send_mail(
                    notification.title,
                    notification.message,
                    settings.DEFAULT_FROM_EMAIL,
                    [notification.user.email],
                    fail_silently=False,
                )
                notification.is_sent_via_email = True
                notification.email_sent_at = timezone.now()
                notification.save()
                count += 1
            except Exception as e:
                self.message_user(request, f'Error sending email to {notification.user.email}: {str(e)}', level='error')
        
        self.message_user(request, f'{count} email(s) sent successfully.')
    send_email_notifications.short_description = 'Send email notifications'


@admin.register(Complaint, site=admin_site)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['complaint_number', 'user', 'category', 'subject', 'status', 
                    'age', 'created_at', 'resolved_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['complaint_number', 'user__username', 'subject', 'description']
    readonly_fields = ['complaint_number', 'created_at', 'updated_at', 'age']
    autocomplete_fields = ['user', 'order', 'seller']
    actions = ['mark_in_progress', 'mark_resolved', 'mark_closed']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Complaint Information', {
            'fields': ('complaint_number', 'user', 'category', 'subject', 'description', 'age')
        }),
        ('Related Items', {
            'fields': ('order', 'seller'),
            'classes': ('collapse',)
        }),
        ('Status & Resolution', {
            'fields': ('status', 'admin_notes', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def age(self, obj):
        """Complaint age"""
        delta = timezone.now() - obj.created_at
        if delta.days > 0:
            return f"{delta.days} days"
        hours = delta.seconds // 3600
        return f"{hours} hours"
    age.short_description = 'Age'
    
    def mark_in_progress(self, request, queryset):
        """Mark complaints as in progress"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} complaint(s) marked as in progress.')
    mark_in_progress.short_description = 'Mark as in progress'
    
    def mark_resolved(self, request, queryset):
        """Mark complaints as resolved"""
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{updated} complaint(s) marked as resolved.')
    mark_resolved.short_description = 'Mark as resolved'
    
    def mark_closed(self, request, queryset):
        """Close complaints"""
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} complaint(s) closed.')
    mark_closed.short_description = 'Close complaints'


@admin.register(PaymentViolation, site=admin_site)
class PaymentViolationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_number', 'auction_product', 'payment_deadline', 'violation_date', 'days_overdue']
    list_filter = ['violation_date', 'payment_deadline']
    search_fields = ['user__username', 'order__order_number', 'auction__product__name']
    readonly_fields = ['violation_date', 'days_overdue']
    autocomplete_fields = ['user', 'auction', 'order']
    date_hierarchy = 'violation_date'
    
    def order_number(self, obj):
        """Display order number"""
        return obj.order.order_number
    order_number.short_description = 'Order'
    
    def auction_product(self, obj):
        """Display auction product"""
        return obj.auction.product.name
    auction_product.short_description = 'Product'
    
    def days_overdue(self, obj):
        """Days overdue"""
        delta = timezone.now() - obj.payment_deadline
        return f"{delta.days} days"
    days_overdue.short_description = 'Days Overdue'


@admin.register(SellerProfile, site=admin_site)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'brand_name', 'is_verified', 'average_rating', 
                    'total_feedbacks', 'total_products', 'total_revenue']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'brand_name', 'business_address_text', 'biography']
    readonly_fields = ['average_rating', 'total_feedbacks', 'created_at', 'updated_at', 
                       'total_products', 'total_revenue', 'total_sales']
    autocomplete_fields = ['user', 'business_address_id']
    actions = ['verify_sellers', 'unverify_sellers', 'update_ratings']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'brand_name', 'biography', 'is_verified')
        }),
        ('Contact & Address', {
            'fields': ('business_address_id', 'business_phone', 'website')
        }),
        ('Social Media', {
            'fields': ('social_media_links',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_feedbacks', 'total_products', 
                      'total_revenue', 'total_sales'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_products(self, obj):
        """Total products listed"""
        return obj.user.products.count()
    total_products.short_description = 'Products'
    
    def total_revenue(self, obj):
        """Total revenue earned"""
        revenue = obj.user.sales.filter(
            status__in=['paid', 'shipped', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        return f"Rs {revenue:,.2f}"
    total_revenue.short_description = 'Revenue'
    
    def total_sales(self, obj):
        """Total number of sales"""
        return obj.user.sales.filter(status__in=['paid', 'shipped', 'delivered']).count()
    total_sales.short_description = 'Sales'
    
    def verify_sellers(self, request, queryset):
        """Verify selected sellers"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} seller(s) verified.')
    verify_sellers.short_description = 'Verify selected sellers'
    
    def unverify_sellers(self, request, queryset):
        """Unverify selected sellers"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} seller(s) unverified.')
    unverify_sellers.short_description = 'Unverify selected sellers'
    
    def update_ratings(self, request, queryset):
        """Update average ratings"""
        for profile in queryset:
            profile.update_rating()
        self.message_user(request, f'Ratings updated for {queryset.count()} seller(s).')
    update_ratings.short_description = 'Update average ratings'


@admin.register(Wishlist, site=admin_site)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'product_status', 'product_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at']
    autocomplete_fields = ['user', 'product']
    
    def product_status(self, obj):
        """Show if product is still available"""
        if hasattr(obj.product, 'auction'):
            return f"Auction - {obj.product.auction.get_status_display()}"
        elif hasattr(obj.product, 'fixed_price'):
            return f"Fixed - {obj.product.fixed_price.get_status_display()}"
        return "No Listing"
    product_status.short_description = 'Status'
    
    def product_price(self, obj):
        """Show current price"""
        if hasattr(obj.product, 'auction'):
            return f"Rs {obj.product.auction.current_price:,.2f}"
        elif hasattr(obj.product, 'fixed_price'):
            return f"Rs {obj.product.fixed_price.get_current_price():,.2f}"
        return "N/A"
    product_price.short_description = 'Price'


@admin.register(ProductReview, site=admin_site)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'buyer', 'rating', 'title', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'buyer__username', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['product', 'buyer', 'order']
    actions = ['verify_purchases']
    
    def verify_purchases(self, request, queryset):
        """Verify that reviews are from actual purchases"""
        updated = 0
        for review in queryset:
            if review.order:
                review.is_verified_purchase = True
                review.save()
                updated += 1
        self.message_user(request, f'{updated} review(s) verified as purchases.')
    verify_purchases.short_description = 'Verify as purchases'


@admin.register(Cart, site=admin_site)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_items', 'total_value', 'created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'total_value']
    autocomplete_fields = ['user']
    
    def total_items(self, obj):
        """Total items in cart"""
        return obj.get_total_items()
    total_items.short_description = 'Items'
    
    def total_value(self, obj):
        """Total cart value"""
        return f"Rs {obj.get_total_price():,.2f}"
    total_value.short_description = 'Value'


@admin.register(CartItem, site=admin_site)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart_user', 'listing', 'quantity', 'unit_price', 'subtotal', 'is_available', 'added_at']
    list_filter = ['added_at', 'updated_at']
    search_fields = ['cart__user__username', 'listing__product__name']
    readonly_fields = ['added_at', 'updated_at', 'subtotal', 'is_available']
    autocomplete_fields = ['cart', 'listing']
    
    def cart_user(self, obj):
        """Display cart owner"""
        return obj.cart.user.username
    cart_user.short_description = 'User'
    
    def unit_price(self, obj):
        """Current unit price"""
        return f"Rs {obj.listing.get_current_price():,.2f}"
    unit_price.short_description = 'Unit Price'
    
    def subtotal(self, obj):
        """Subtotal for this item"""
        return f"Rs {obj.get_subtotal():,.2f}"
    subtotal.short_description = 'Subtotal'
    
    def is_available(self, obj):
        """Check availability"""
        return obj.is_available()
    is_available.boolean = True
    is_available.short_description = 'Available'


@admin.register(OrderItem, site=admin_site)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'product', 'seller', 'quantity', 'unit_price', 
                    'subtotal', 'is_shipped', 'shipped_at']
    list_filter = ['is_shipped', 'created_at', 'shipped_at']
    search_fields = ['order__order_number', 'product__name', 'product__seller__username']
    readonly_fields = ['subtotal', 'created_at', 'seller']
    autocomplete_fields = ['order', 'product', 'listing']
    actions = ['mark_as_shipped']
    
    def order_number(self, obj):
        """Display order number"""
        return obj.order.order_number
    order_number.short_description = 'Order'
    
    def seller(self, obj):
        """Display seller"""
        return obj.product.seller.username
    seller.short_description = 'Seller'
    
    def mark_as_shipped(self, request, queryset):
        """Mark items as shipped"""
        updated = queryset.filter(is_shipped=False).update(
            is_shipped=True,
            shipped_at=timezone.now()
        )
        
        # Check if all items in related orders are shipped
        for item in queryset:
            item.order.check_and_update_shipping_status()
        
        self.message_user(request, f'{updated} item(s) marked as shipped.')
    mark_as_shipped.short_description = 'Mark as shipped'


@admin.register(SellerTransfer, site=admin_site)
class SellerTransferAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment_order', 'seller', 'amount', 'platform_fee', 'net_amount', 
                    'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at', 'completed_at']
    search_fields = ['seller__username', 'stripe_transfer_id', 'payment__order__order_number']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'net_amount']
    autocomplete_fields = ['payment', 'seller']
    actions = ['retry_failed_transfers']
    date_hierarchy = 'created_at'
    
    def payment_order(self, obj):
        """Display order number"""
        return obj.payment.order.order_number
    payment_order.short_description = 'Order'
    
    def net_amount(self, obj):
        """Amount after platform fee"""
        net = obj.amount - obj.platform_fee
        return f"Rs {net:,.2f}"
    net_amount.short_description = 'Net Amount'
    
    def retry_failed_transfers(self, request, queryset):
        """Retry failed transfers"""
        failed = queryset.filter(status='failed')
        self.message_user(
            request, 
            f'{failed.count()} failed transfer(s) marked for retry. Manual processing required.',
            level='warning'
        )
    retry_failed_transfers.short_description = 'Retry failed transfers'
