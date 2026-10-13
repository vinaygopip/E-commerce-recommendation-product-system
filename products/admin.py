from django.contrib import admin
from .models import Category, Brand, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'discount_percent', 'stock', 'rating_avg', 'view_count', 'is_active', 'is_featured')
    list_filter = ('category', 'brand', 'is_active', 'is_featured', 'created_at')
    list_editable = ('price', 'discount_percent', 'stock', 'is_active', 'is_featured')
    search_fields = ('name', 'description', 'features')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
