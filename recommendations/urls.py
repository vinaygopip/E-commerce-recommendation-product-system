from django.urls import path
from . import views

urlpatterns = [
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle_view, name='wishlist_toggle'),
    path('wishlist/move-to-cart/<int:product_id>/', views.wishlist_move_to_cart_view, name='wishlist_move_to_cart'),
    path('ai-recommendations/', views.recommendations_page_view, name='recommendations_showcase'),
    path('cross-platform/', views.cross_platform_explorer_view, name='cross_platform_deals'),
]
