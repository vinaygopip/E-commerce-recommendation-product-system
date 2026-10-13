from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Wishlist(models.Model):
    user = models.OneToOneField(User, related_name='wishlist', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlisted_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wishlist', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s Wishlist"


class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('VIEW', 'Product View'),
        ('CLICK', 'Product Click'),
        ('SEARCH', 'Search Query'),
        ('WISHLIST_ADD', 'Added to Wishlist'),
        ('CART_ADD', 'Added to Cart'),
        ('PURCHASE', 'Purchased Product'),
        ('RATING', 'Rated Product'),
    )

    ACTIVITY_WEIGHTS = {
        'VIEW': 1.0,
        'CLICK': 1.5,
        'SEARCH': 1.0,
        'WISHLIST_ADD': 3.0,
        'CART_ADD': 4.0,
        'PURCHASE': 6.0,
        'RATING': 5.0,
    }

    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=50, blank=True, null=True)
    product = models.ForeignKey(Product, related_name='activities', on_delete=models.CASCADE, null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    search_query = models.CharField(max_length=255, blank=True, null=True)
    score_weight = models.FloatField(default=1.0)
    rating_value = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['product', 'activity_type']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.score_weight and self.activity_type in self.ACTIVITY_WEIGHTS:
            self.score_weight = self.ACTIVITY_WEIGHTS[self.activity_type]
        super().save(*args, **kwargs)

    def __str__(self):
        usr = self.user.username if self.user else f"Guest ({self.session_key[:8] if self.session_key else 'anon'})"
        prod = self.product.name if self.product else (self.search_query or 'N/A')
        return f"{usr} -> {self.activity_type} on {prod} (weight: {self.score_weight})"


class RecommendationFeedback(models.Model):
    """Logs recommendations shown and clicked for CTR analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    algorithm_type = models.CharField(max_length=30, choices=[
        ('CONTENT_BASED', 'Content Based'),
        ('COLLABORATIVE', 'Collaborative Filtering'),
        ('HYBRID', 'Hybrid Model'),
        ('COLD_START', 'Cold Start / Popularity'),
    ])
    explanation = models.CharField(max_length=255, blank=True)
    clicked = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Rec: {self.product.name} ({self.algorithm_type}) clicked={self.clicked}"


class PlatformDeal(models.Model):
    PLATFORM_CHOICES = (
        ('Amazon', 'Amazon'),
        ('Flipkart', 'Flipkart'),
        ('Croma', 'Croma'),
        ('Reliance Digital', 'Reliance Digital'),
        ('Tata CLiQ', 'Tata CLiQ'),
        ('Myntra', 'Myntra'),
    )

    product = models.ForeignKey(Product, related_name='platform_deals', on_delete=models.CASCADE)
    platform_name = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    platform_product_title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_url = models.URLField(max_length=500, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.5)
    rating_count = models.PositiveIntegerField(default=120)
    delivery_info = models.CharField(max_length=100, default='Standard Delivery (2-3 Days)')
    similarity_score = models.FloatField(default=0.95, help_text="Similarity percentage match with internal product")
    in_stock = models.BooleanField(default=True)
    badge_text = models.CharField(max_length=100, blank=True, help_text="e.g. 'Lowest Price', 'Fastest Delivery', 'Amazon Choice'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']
        unique_together = ('product', 'platform_name')

    def __str__(self):
        return f"{self.platform_name}: {self.product.name} - ₹{self.price}"

    @property
    def platform_color(self):
        colors = {
            'Amazon': '#FF9900',
            'Flipkart': '#2874F0',
            'Croma': '#00B5B5',
            'Reliance Digital': '#E42529',
            'Tata CLiQ': '#000000',
            'Myntra': '#FF3F6C',
        }
        return colors.get(self.platform_name, '#2563EB')

    @property
    def platform_icon(self):
        icons = {
            'Amazon': 'bi-cart-check',
            'Flipkart': 'bi-lightning-charge',
            'Croma': 'bi-tv',
            'Reliance Digital': 'bi-plug',
            'Tata CLiQ': 'bi-gem',
            'Myntra': 'bi-bag-heart',
        }
        return icons.get(self.platform_name, 'bi-shop')

