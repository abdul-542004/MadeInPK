from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Register viewsets
router.register(r'provinces', views.ProvinceViewSet, basename='province')
router.register(r'cities', views.CityViewSet, basename='city')
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'auctions', views.AuctionListingViewSet, basename='auction')
router.register(r'listings', views.FixedPriceListingViewSet, basename='listing')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'feedbacks', views.FeedbackViewSet, basename='feedback')
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'complaints', views.ComplaintViewSet, basename='complaint')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')
router.register(r'seller-profiles', views.SellerProfileViewSet, basename='seller-profile')
router.register(r'product-reviews', views.ProductReviewViewSet, basename='product-review')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'stripe/connect', views.StripeConnectViewSet, basename='stripe-connect')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/profile/', views.profile, name='profile'),
    path('auth/become-seller/', views.become_seller, name='become-seller'),
    
    # Seller statistics
    path('seller/statistics/', views.seller_statistics, name='seller-statistics'),
    path('seller/earnings/', views.seller_earnings, name='seller-earnings'),
    path('seller/transactions/', views.seller_transactions, name='seller-transactions'),
    path('seller/product-performance/', views.product_performance, name='product-performance'),
    
    # Stripe webhook
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
    
    # Admin tools
    path('admin/trigger-transfers/', views.admin_trigger_transfers, name='admin-trigger-transfers'),
    path('admin/orders-needing-transfers/', views.admin_orders_needing_transfers, name='admin-orders-needing-transfers'),
    
    # Payment pages
    path('payments/success/', views.payment_success, name='payment-success'),
    path('payments/cancel/', views.payment_cancel, name='payment-cancel'),
    
    # Router URLs
    path('', include(router.urls)),
]
