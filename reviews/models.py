from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.db.models import Avg

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)], default=5)
    title = models.CharField(max_length=150)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.rating}★ by {self.user.username} for {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_product_rating()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        # Recalculate rating
        reviews = product.reviews.all()
        if reviews.exists():
            avg = reviews.aggregate(Avg('rating'))['rating__avg']
            product.rating_avg = round(avg, 2)
            product.rating_count = reviews.count()
        else:
            product.rating_avg = 0.0
            product.rating_count = 0
        product.save()

    def update_product_rating(self):
        reviews = self.product.reviews.all()
        avg = reviews.aggregate(Avg('rating'))['rating__avg'] or self.rating
        self.product.rating_avg = round(avg, 2)
        self.product.rating_count = reviews.count()
        self.product.save()
