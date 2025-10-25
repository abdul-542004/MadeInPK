from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Province, City, Address, Category, Product, ProductImage,
    AuctionListing, Bid, FixedPriceListing, Order, Payment,
    Feedback, Conversation, Message, Notification, Complaint, PaymentViolation
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_blocked', 'failed_payment_count', 'created_at']
    list_filter = ['role', 'is_blocked', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'role', 'is_blocked', 'failed_payment_count', 
                      'stripe_customer_id', 'stripe_account_id')
        }),
    )


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'province']
    list_filter = ['province']
    search_fields = ['name']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'street_address', 'city', 'postal_code', 'is_default']
    list_filter = ['is_default', 'city']
    search_fields = ['user__username', 'street_address']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent']
    search_fields = ['name']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'seller', 'category', 'condition', 'created_at']
    list_filter = ['condition', 'category', 'created_at']
    search_fields = ['name', 'description', 'seller__username']
    inlines = [ProductImageInline]


@admin.register(AuctionListing)
class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'starting_price', 'current_price', 'status', 
                    'start_time', 'end_time', 'winner']
    list_filter = ['status', 'start_time', 'end_time']
    search_fields = ['product__name', 'winner__username']
    readonly_fields = ['current_price', 'winner']


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['id', 'auction', 'bidder', 'amount', 'bid_time', 'is_winning']
    list_filter = ['is_winning', 'bid_time']
    search_fields = ['auction__product__name', 'bidder__username']
    readonly_fields = ['bid_time']


@admin.register(FixedPriceListing)
class FixedPriceListingAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'price', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['product__name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'buyer', 'seller', 'product', 'order_type', 
                    'total_amount', 'status', 'created_at']
    list_filter = ['order_type', 'status', 'created_at']
    search_fields = ['order_number', 'buyer__username', 'seller__username', 'product__name']
    readonly_fields = ['order_number', 'platform_fee', 'seller_amount', 'created_at', 
                      'paid_at', 'shipped_at', 'delivered_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'stripe_payment_intent_id']
    readonly_fields = ['created_at', 'completed_at']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'buyer', 'seller', 'seller_rating', 
                    'platform_rating', 'created_at']
    list_filter = ['seller_rating', 'platform_rating', 'product_as_described', 'created_at']
    search_fields = ['buyer__username', 'seller__username', 'order__order_number']
    readonly_fields = ['created_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'seller', 'order', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['buyer__username', 'seller__username']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'content']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notification_type', 'title', 'is_read', 
                    'is_sent_via_email', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_sent_via_email', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'email_sent_at']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['complaint_number', 'user', 'category', 'subject', 'status', 
                    'created_at', 'resolved_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['complaint_number', 'user__username', 'subject', 'description']
    readonly_fields = ['complaint_number', 'created_at', 'updated_at']


@admin.register(PaymentViolation)
class PaymentViolationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order', 'payment_deadline', 'violation_date']
    list_filter = ['violation_date']
    search_fields = ['user__username', 'order__order_number']
    readonly_fields = ['violation_date']

