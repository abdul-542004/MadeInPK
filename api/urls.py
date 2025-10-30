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

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/profile/', views.profile, name='profile'),
    path('auth/become-seller/', views.become_seller, name='become-seller'),
    
    # Router URLs
    path('', include(router.urls)),
]
