from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category, Brand
from recommendations.engine import (
    recommend_for_user,
    recommend_similar_products,
    get_customers_also_bought,
    get_trending_products,
    get_recently_viewed,
    log_user_activity
)
from reviews.models import Review
from orders.models import OrderItem
from recommendations.cross_platform import get_cross_platform_deals

def landing_view(request):
    """
    Dedicated landing page presenting the AI Recommendation E-Commerce Platform.
    Features hero showcase matching reference UI with quick access to Login, Register, Storefront, and ML details.
    """
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    categories = Category.objects.all()[:6]
    trending_products = get_trending_products(limit=4)
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'categories': categories,
        'trending_products': trending_products,
    }
    return render(request, 'products/landing.html', context)


def home_view(request):
    """
    Personalized intelligent homepage:
    Blends Hybrid recommendations, trending products, recently viewed items, and categories.
    """
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    # Recommendations for this specific user or session
    hybrid_recs = recommend_for_user(user=request.user, session_key=session_key, limit=8)
    
    # Trending & Popular items
    trending_products = get_trending_products(limit=8)

    # Recently viewed
    recently_viewed = get_recently_viewed(user=request.user, session_key=session_key, limit=6)

    # New arrivals
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    # Special offers (highest discount)
    special_deals = Product.objects.filter(is_active=True, discount_percent__gt=10).order_by('-discount_percent')[:4]

    categories = Category.objects.all()[:6]

    context = {
        'hybrid_recs': hybrid_recs,
        'trending_products': trending_products,
        'recently_viewed': recently_viewed,
        'new_arrivals': new_arrivals,
        'special_deals': special_deals,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)


def product_list_view(request, category_slug=None):
    """
    Full product catalog browsing with multi-faceted filtering, search, sorting, and pagination.
    """
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    products = Product.objects.filter(is_active=True).select_related('category', 'brand')
    categories = Category.objects.all()
    brands = Brand.objects.all()

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    # Search keyword
    query = request.GET.get('q', '').strip()
    if query:
        # Log search activity for ML personalization
        log_user_activity(
            user=request.user,
            session_key=session_key,
            activity_type='SEARCH',
            search_query=query
        )
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(features__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Category filter dropdown
    cat_filter = request.GET.get('category')
    if cat_filter:
        products = products.filter(category__slug=cat_filter)

    # Brand filter
    brand_filter = request.GET.get('brand')
    if brand_filter:
        products = products.filter(brand__slug=brand_filter)

    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Rating filter
    min_rating = request.GET.get('rating')
    if min_rating:
        try:
            products = products.filter(rating_avg__gte=float(min_rating))
        except ValueError:
            pass

    # Stock filter
    in_stock = request.GET.get('in_stock')
    if in_stock == '1':
        products = products.filter(stock__gt=0)

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating_avg', '-rating_count')
    elif sort == 'popularity':
        products = products.order_by('-view_count')
    else: # newest
        products = products.order_by('-created_at')

    # Pagination: 12 products per page
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'current_category': current_category,
        'query': query,
        'selected_sort': sort,
        'selected_cat': cat_filter,
        'selected_brand': brand_filter,
        'min_price': min_price,
        'max_price': max_price,
        'selected_rating': min_rating,
        'total_count': paginator.count,
    }
    return render(request, 'products/product_list.html', context)


def product_detail_view(request, slug):
    """
    Product details page with:
    - Content-Based recommendations ('Similar Products')
    - Collaborative Filtering recommendations ('Customers Also Bought')
    - Ratings and reviews
    - Automatic user view activity logging
    """
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    product = get_object_or_404(Product.objects.select_related('category', 'brand'), slug=slug, is_active=True)

    # Log user view activity to drive recommendation engine
    log_user_activity(
        user=request.user,
        session_key=session_key,
        product=product,
        activity_type='VIEW'
    )

    # 1. Content-Based Recommendations (Similar features/category/brand)
    similar_products = recommend_similar_products(product, limit=4)

    # 2. Collaborative Filtering Recommendations (Items frequently bought/interacted together)
    also_bought_products = get_customers_also_bought(product, limit=4)

    # 3. Cross-Platform Price Comparison & Similar Deals (Amazon, Flipkart, Croma, Myntra, etc.)
    cross_platform_deals = get_cross_platform_deals(product)

    # Reviews and ratings
    reviews = product.reviews.all().select_related('user')
    user_review = None
    has_purchased = False

    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        has_purchased = OrderItem.objects.filter(order__user=request.user, product=product).exists()

    # Features list parsed into lines
    features_list = [f.strip() for f in (product.features or '').split('\n') if f.strip()]
    if not features_list and product.features:
        features_list = [f.strip() for f in product.features.split(',') if f.strip()]

    context = {
        'product': product,
        'similar_products': similar_products,
        'also_bought_products': also_bought_products,
        'cross_platform_deals': cross_platform_deals,
        'reviews': reviews,
        'user_review': user_review,
        'has_purchased': has_purchased,
        'features_list': features_list,
    }
    return render(request, 'products/product_detail.html', context)
