"""
Custom Admin Dashboard Views with Statistics and Charts
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from .models import (
    User, Product, AuctionListing, FixedPriceListing, Order, 
    Payment, Feedback, Category, SellerProfile, ProductReview,
    OrderItem
)


@staff_member_required
def admin_dashboard(request):
    """
    Main admin dashboard with comprehensive statistics and charts
    """
    # Time filters
    today = timezone.now()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)
    
    # ==================== OVERVIEW STATISTICS ====================
    
    # User Statistics
    total_users = User.objects.count()
    total_buyers = User.objects.filter(Q(role='buyer') | Q(role='both')).count()
    total_sellers = User.objects.filter(Q(role='seller') | Q(role='both')).count()
    new_users_this_month = User.objects.filter(created_at__gte=month_ago).count()
    blocked_users = User.objects.filter(is_blocked=True).count()
    
    # Product Statistics
    total_products = Product.objects.count()
    active_auction_listings = AuctionListing.objects.filter(status='active').count()
    active_fixed_price_listings = FixedPriceListing.objects.filter(status='active').count()
    total_active_listings = active_auction_listings + active_fixed_price_listings
    products_this_month = Product.objects.filter(created_at__gte=month_ago).count()
    
    # Order Statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending_payment').count()
    completed_orders = Order.objects.filter(status='delivered').count()
    orders_this_month = Order.objects.filter(created_at__gte=month_ago).count()
    
    # Revenue Statistics
    total_revenue = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    platform_fees = Order.objects.filter(status='delivered').aggregate(
        total=Sum('platform_fee')
    )['total'] or Decimal('0.00')
    
    revenue_this_month = Order.objects.filter(
        status='delivered',
        delivered_at__gte=month_ago
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Average Order Value
    avg_order_value = Order.objects.filter(status='delivered').aggregate(
        avg=Avg('total_amount')
    )['avg'] or Decimal('0.00')
    
    # Seller Statistics
    verified_sellers = SellerProfile.objects.filter(is_verified=True).count()
    total_seller_profiles = SellerProfile.objects.count()
    
    # Rating Statistics
    avg_seller_rating = Feedback.objects.aggregate(avg=Avg('seller_rating'))['avg'] or 0
    avg_platform_rating = Feedback.objects.aggregate(avg=Avg('platform_rating'))['avg'] or 0
    total_feedbacks = Feedback.objects.count()
    
    # ==================== CHARTS DATA ====================
    
    # 1. Orders by Status (Pie Chart)
    orders_by_status = list(Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count'))
    
    # 2. Revenue Trend (Last 30 Days - Line Chart)
    revenue_trend = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        daily_revenue = Order.objects.filter(
            status='delivered',
            delivered_at__gte=day_start,
            delivered_at__lt=day_end
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        revenue_trend.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'revenue': float(daily_revenue)
        })
    
    # 3. Orders per Day (Last 30 Days - Line Chart)
    orders_trend = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        daily_orders = Order.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        ).count()
        
        orders_trend.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'orders': daily_orders
        })
    
    # 4. Top Categories (Bar Chart)
    top_categories = list(Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:10].values('name', 'product_count'))
    
    # 5. Best Selling Products (Top 10)
    best_selling_products = list(Product.objects.annotate(
        total_sold=Count('orders', filter=Q(orders__status='delivered'))
    ).filter(total_sold__gt=0).order_by('-total_sold')[:10].values(
        'id', 'name', 'total_sold', 'seller__username'
    ))
    
    # 6. Top Sellers by Revenue
    top_sellers = list(User.objects.filter(
        Q(role='seller') | Q(role='both')
    ).annotate(
        total_revenue=Sum('sales__total_amount', filter=Q(sales__status='delivered'))
    ).filter(total_revenue__gt=0).order_by('-total_revenue')[:10].values(
        'id', 'username', 'email', 'total_revenue'
    ))
    
    # 7. Order Type Distribution
    order_type_distribution = list(Order.objects.values('order_type').annotate(
        count=Count('id')
    ))
    
    # 8. Product Condition Distribution
    condition_distribution = list(Product.objects.values('condition').annotate(
        count=Count('id')
    ))
    
    # 9. User Registration Trend (Last 12 Months)
    user_registration_trend = []
    for i in range(11, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        if i > 0:
            month_end = (today.replace(day=1) - timedelta(days=30*(i-1))).replace(day=1)
        else:
            month_end = today
        
        monthly_users = User.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        user_registration_trend.append({
            'month': month_start.strftime('%b %Y'),
            'users': monthly_users
        })
    
    # 10. Average Ratings Comparison
    rating_comparison = {
        'seller_rating': float(avg_seller_rating) if avg_seller_rating else 0,
        'platform_rating': float(avg_platform_rating) if avg_platform_rating else 0,
    }
    
    # 11. Top Rated Sellers
    top_rated_sellers = list(SellerProfile.objects.filter(
        total_feedbacks__gte=5
    ).order_by('-average_rating')[:10].values(
        'user__username', 'average_rating', 'total_feedbacks', 'brand_name'
    ))
    
    # 12. Recent Activity (Last 10 Orders)
    recent_orders = Order.objects.select_related(
        'buyer', 'seller', 'product'
    ).order_by('-created_at')[:10]
    
    # ==================== ALERTS & WARNINGS ====================
    alerts = []
    
    # Pending payments
    if pending_orders > 0:
        alerts.append({
            'type': 'warning',
            'message': f'{pending_orders} orders pending payment'
        })
    
    # Blocked users
    if blocked_users > 0:
        alerts.append({
            'type': 'danger',
            'message': f'{blocked_users} users are currently blocked'
        })
    
    # Low platform rating
    if avg_platform_rating and avg_platform_rating < 3.5:
        alerts.append({
            'type': 'danger',
            'message': f'Platform rating is low: {avg_platform_rating:.2f}/5.00'
        })
    
    # Check for orders needing shipment
    paid_not_shipped = Order.objects.filter(status='paid').count()
    if paid_not_shipped > 0:
        alerts.append({
            'type': 'info',
            'message': f'{paid_not_shipped} paid orders awaiting shipment'
        })
    
    context = {
        # Overview Stats
        'total_users': total_users,
        'total_buyers': total_buyers,
        'total_sellers': total_sellers,
        'new_users_this_month': new_users_this_month,
        'blocked_users': blocked_users,
        
        'total_products': total_products,
        'total_active_listings': total_active_listings,
        'active_auction_listings': active_auction_listings,
        'active_fixed_price_listings': active_fixed_price_listings,
        'products_this_month': products_this_month,
        
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'orders_this_month': orders_this_month,
        
        'total_revenue': total_revenue,
        'platform_fees': platform_fees,
        'revenue_this_month': revenue_this_month,
        'avg_order_value': avg_order_value,
        
        'verified_sellers': verified_sellers,
        'total_seller_profiles': total_seller_profiles,
        
        'avg_seller_rating': avg_seller_rating,
        'avg_platform_rating': avg_platform_rating,
        'total_feedbacks': total_feedbacks,
        
        # Charts Data (as JSON)
        'orders_by_status_json': json.dumps(orders_by_status),
        'revenue_trend_json': json.dumps(revenue_trend, default=str),
        'orders_trend_json': json.dumps(orders_trend),
        'top_categories_json': json.dumps(top_categories),
        'best_selling_products': best_selling_products,
        'top_sellers': top_sellers,
        'order_type_distribution_json': json.dumps(order_type_distribution),
        'condition_distribution_json': json.dumps(condition_distribution),
        'user_registration_trend_json': json.dumps(user_registration_trend),
        'rating_comparison_json': json.dumps(rating_comparison),
        'top_rated_sellers': top_rated_sellers,
        'recent_orders': recent_orders,
        
        # Alerts
        'alerts': alerts,
    }
    
    return render(request, 'admin/dashboard.html', context)
