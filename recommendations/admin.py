from django.contrib import admin
from .models import Wishlist, WishlistItem, UserActivity, RecommendationFeedback, PlatformDeal

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'product', 'activity_type', 'score_weight', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'product__name', 'search_query')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')

@admin.register(RecommendationFeedback)
class RecommendationFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'algorithm_type', 'clicked', 'purchased', 'created_at')
    list_filter = ('algorithm_type', 'clicked', 'purchased')

@admin.register(PlatformDeal)
class PlatformDealAdmin(admin.ModelAdmin):
    list_display = ('product', 'platform_name', 'price', 'rating', 'similarity_score', 'in_stock', 'updated_at')
    list_filter = ('platform_name', 'in_stock')
    search_fields = ('product__name', 'platform_product_title')
    list_editable = ('price', 'in_stock')
