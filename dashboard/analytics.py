from django.contrib.auth.models import User
from products.models import Product, Category
from orders.models import Order, OrderItem
from reviews.models import Review
from recommendations.models import UserActivity, RecommendationFeedback
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
import json

def get_dashboard_metrics():
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    total_users = User.objects.count()
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    
    revenue_agg = Order.objects.filter(payment_status='Paid').aggregate(Sum('total_amount'))
    total_revenue = revenue_agg['total_amount__sum'] or 0.0

    total_reviews = Review.objects.count()
    avg_store_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0.0

    # User interactions
    total_activities = UserActivity.objects.count()
    total_views = UserActivity.objects.filter(activity_type='VIEW').count()
    total_purchases = UserActivity.objects.filter(activity_type='PURCHASE').count()
    
    conversion_rate = round((total_purchases / total_views * 100), 2) if total_views > 0 else 0.0

    # Top Viewed Products
    top_viewed_products = Product.objects.filter(is_active=True).order_by('-view_count')[:6]

    # Top Selling Products (by quantity ordered)
    top_selling = OrderItem.objects.values('product__name', 'product__id', 'product__price')\
        .annotate(total_sold=Sum('quantity'))\
        .order_by('-total_sold')[:6]

    # Category distribution for Pie / Doughnut Chart
    cat_distribution = Category.objects.annotate(product_count=Count('products')).values('name', 'product_count')
    cat_labels = [c['name'] for c in cat_distribution]
    cat_counts = [c['product_count'] for c in cat_distribution]

    # Activity breakdown for Radar / Bar Chart
    activity_counts = UserActivity.objects.values('activity_type').annotate(count=Count('id')).order_by('-count')
    activity_labels = [a['activity_type'] for a in activity_counts]
    activity_data = [a['count'] for a in activity_counts]

    # Recent 7 days sales timeline
    sales_labels = []
    sales_revenue = []
    sales_order_counts = []
    for i in range(6, -1, -1):
        day_date = (now - timedelta(days=i)).date()
        day_orders = Order.objects.filter(created_at__date=day_date)
        day_rev = day_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.0
        
        sales_labels.append(day_date.strftime('%b %d'))
        sales_revenue.append(float(day_rev))
        sales_order_counts.append(day_orders.count())

    # Recent Orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]

    # Conversion Funnel counts
    funnel_views = total_views
    funnel_wishlist = UserActivity.objects.filter(activity_type='WISHLIST_ADD').count()
    funnel_cart = UserActivity.objects.filter(activity_type='CART_ADD').count()
    funnel_purchase = total_purchases

    # Complete Details for Bottom Drilldown
    all_users_list = User.objects.annotate(
        order_count=Count('orders', distinct=True),
        activity_count=Count('activities', distinct=True),
        review_count=Count('reviews', distinct=True)
    ).order_by('-date_joined')

    all_products_list = Product.objects.select_related('category', 'brand').order_by('-created_at')

    all_orders_list = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')

    return {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'total_reviews': total_reviews,
        'avg_store_rating': round(avg_store_rating, 1),
        'total_activities': total_activities,
        'conversion_rate': conversion_rate,
        'top_viewed_products': top_viewed_products,
        'top_selling': top_selling,
        'recent_orders': recent_orders,
        # Complete record lists for detailed views
        'all_users_list': all_users_list,
        'all_products_list': all_products_list,
        'all_orders_list': all_orders_list,
        # Chart JSON data
        'cat_labels_json': json.dumps(cat_labels),
        'cat_counts_json': json.dumps(cat_counts),
        'activity_labels_json': json.dumps(activity_labels),
        'activity_data_json': json.dumps(activity_data),
        'sales_labels_json': json.dumps(sales_labels),
        'sales_revenue_json': json.dumps(sales_revenue),
        'sales_order_counts_json': json.dumps(sales_order_counts),
        'funnel_data_json': json.dumps([funnel_views, funnel_wishlist, funnel_cart, funnel_purchase]),
    }

