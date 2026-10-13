from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.id} ({self.user.username if self.user else 'Guest'})"

    def get_total_price(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_total_regular_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def get_total_savings(self):
        return self.get_total_regular_price() - self.get_total_price()

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_subtotal(self):
        return self.product.discounted_price * self.quantity
