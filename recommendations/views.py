from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Wishlist, WishlistItem
from products.models import Product, Category
from cart.views import get_or_create_cart
from cart.models import CartItem
from .engine import (
    log_user_activity,
    recommend_for_user,
    recommend_similar_products,
    get_trending_products
)
from .content_based import content_recommender
from .collaborative import collaborative_recommender
from .hybrid import hybrid_recommender

@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product', 'product__category').all()
    return render(request, 'recommendations/wishlist.html', {'wishlist': wishlist, 'items': items})


@login_required
def wishlist_toggle_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    
    item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
    added = False
    if item:
        item.delete()
        added = False
        message = f"Removed '{product.name}' from your wishlist."
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        added = True
        message = f"Added '{product.name}' to your wishlist."

        # Log WISHLIST_ADD user activity to update recommendation models
        log_user_activity(
            user=request.user,
            session_key=request.session.session_key,
            product=product,
            activity_type='WISHLIST_ADD'
        )

    wishlist_count = wishlist.items.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'added': added,
            'message': message,
            'wishlist_count': wishlist_count
        })

    if added:
        messages.success(request, message)
    else:
        messages.info(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


@login_required
def wishlist_move_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.objects.filter(user=request.user).first()
    if wishlist:
        WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Log CART_ADD
    log_user_activity(
        user=request.user,
        session_key=request.session.session_key,
        product=product,
        activity_type='CART_ADD'
    )

    messages.success(request, f"Moved '{product.name}' to your cart.")
    return redirect('cart_detail')


def recommendations_page_view(request):
    """
    Dedicated AI Recommendation & Cross-Platform Engine:
    Allows user to input any product name to compare across platforms (Amazon, Flipkart, Croma, etc.)
    and suggests the best recommended product with the optimal price and rating.
    """
    from .cross_platform import get_ai_multiplatform_product_analysis

    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    query = request.GET.get('q', '').strip()
    product_id = request.GET.get('product_id', '')

    # Run AI Cross-Platform Analysis
    ai_analysis = get_ai_multiplatform_product_analysis(
        query_text=query,
        product_id=int(product_id) if product_id.isdigit() else None
    )

    # 1. Personalized Hybrid Recommendations
    hybrid_recs = recommend_for_user(user=request.user, session_key=session_key, limit=6)

    # Quick Search Store Catalog collection & categories
    all_catalog_products = Product.objects.filter(is_active=True).select_related('category').order_by('-view_count')
    catalog_categories = Category.objects.filter(products__is_active=True).distinct().order_by('name')

    # Catalog sample products for quick-click suggestions
    catalog_suggestions = all_catalog_products[:6]

    # ML Architecture Status
    collab_status = "Trained & Active" if collaborative_recommender.item_sim_df is not None else "Needs Training"
    content_status = "Trained & Active" if content_recommender.tfidf_matrix is not None else "Needs Training"

    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = list(WishlistItem.objects.filter(wishlist__user=request.user).values_list('product_id', flat=True))

    context = {
        'query': query,
        'selected_product_id': int(product_id) if product_id.isdigit() else None,
        'ai_analysis': ai_analysis,
        'hybrid_recs': hybrid_recs,
        'catalog_suggestions': catalog_suggestions,
        'all_catalog_products': all_catalog_products,
        'catalog_categories': catalog_categories,
        'total_catalog_count': all_catalog_products.count(),
        'user_wishlist_ids': user_wishlist_ids,
        'collab_status': collab_status,
        'content_status': content_status,
        'weights': {
            'content': int(hybrid_recommender.w_content * 100),
            'affinity': int(hybrid_recommender.w_user_affinity * 100),
            'collab': int(hybrid_recommender.w_collab * 100),
            'popularity': int(hybrid_recommender.w_popularity * 100),
        }
    }
    return render(request, 'recommendations/showcase.html', context)


def cross_platform_explorer_view(request):
    """
    Explore and compare real-time prices & recommendations across external platforms
    (Amazon, Flipkart, Croma, Reliance Digital, Myntra, Tata CLiQ).
    """
    from .cross_platform import get_cross_platform_deals

    selected_platform = request.GET.get('platform', '')
    sort_by = request.GET.get('sort', 'savings')

    products = Product.objects.filter(is_active=True).select_related('category', 'brand')
    
    all_deals = []
    for prod in products:
        cp_data = get_cross_platform_deals(prod)
        for deal in cp_data['deals']:
            if not selected_platform or deal['platform_name'] == selected_platform:
                all_deals.append({
                    'product': prod,
                    'deal': deal,
                    'store_price': cp_data['store_price'],
                    'savings_on_store': deal['savings_on_store'],
                    'is_store_cheaper': deal['is_store_cheaper'],
                    'is_external_cheaper': deal['is_external_cheaper'],
                })

    # Sorting
    if sort_by == 'savings':
        all_deals.sort(key=lambda x: x['deal']['savings_on_store'], reverse=True)
    elif sort_by == 'price_asc':
        all_deals.sort(key=lambda x: x['deal']['price'])
    elif sort_by == 'similarity':
        all_deals.sort(key=lambda x: x['deal']['similarity_score'], reverse=True)

    platforms = ['Amazon', 'Flipkart', 'Croma', 'Reliance Digital', 'Myntra', 'Tata CLiQ']

    context = {
        'deals_list': all_deals[:30],
        'total_deals_count': len(all_deals),
        'platforms': platforms,
        'selected_platform': selected_platform,
        'selected_sort': sort_by,
    }
    return render(request, 'recommendations/cross_platform.html', context)
