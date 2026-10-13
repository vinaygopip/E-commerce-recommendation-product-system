"""
Unified Recommendation Engine Facade
Provides clean, high-level recommendation and activity logging APIs
for Django views and background tasks.
"""

from products.models import Product
from recommendations.models import UserActivity, RecommendationFeedback
from .content_based import content_recommender
from .collaborative import collaborative_recommender
from .hybrid import hybrid_recommender
from django.db.models import F

def log_user_activity(user=None, session_key=None, product=None, activity_type='VIEW', search_query=None, rating_value=None):
    """
    Records a user interaction event to drive the real-time ML recommendation models.
    """
    user_obj = user if (user and user.is_authenticated) else None
    
    # If product view, increment product view_count
    if activity_type in ['VIEW', 'CLICK'] and product:
        Product.objects.filter(pk=product.pk).update(view_count=F('view_count') + 1)

    activity = UserActivity.objects.create(
        user=user_obj,
        session_key=session_key,
        product=product,
        activity_type=activity_type,
        search_query=search_query,
        rating_value=rating_value
    )
    return activity


def recommend_for_user(user=None, session_key=None, limit=8):
    """
    Master function: Returns personalized Hybrid recommendations with explanation strings.
    """
    recommendations = hybrid_recommender.recommend(user=user, session_key=session_key, limit=limit)
    return recommendations


def recommend_similar_products(product, limit=4):
    """
    Content-Based Filtering: Finds products with similar category, brand, features, and descriptions.
    """
    if not product:
        return []
    sim_items = content_recommender.get_similar_products(product.id, top_n=limit)
    
    results = []
    for pid, score in sim_items:
        try:
            p = Product.objects.select_related('category', 'brand').get(id=pid, is_active=True)
            results.append({
                'product': p,
                'score': round(score, 3),
                'algorithm': 'CONTENT_BASED',
                'explanation': f"Similar specifications & brand to {product.name[:30]}"
            })
        except Product.DoesNotExist:
            continue
    
    # Fallback to category products if TF-IDF scores are scarce
    if len(results) < limit:
        existing_ids = [r['product'].id for r in results] + [product.id]
        cat_fillers = Product.objects.filter(category=product.category, is_active=True).exclude(id__in=existing_ids)[:limit - len(results)]
        for p in cat_fillers:
            results.append({
                'product': p,
                'score': 0.5,
                'algorithm': 'CATEGORY_MATCH',
                'explanation': f"Popular in same category ({product.category.name})"
            })

    return results


def get_customers_also_bought(product, limit=4):
    """
    Collaborative Filtering: Discovers products frequently interacted/purchased together.
    """
    if not product:
        return []
    collab_items = collaborative_recommender.get_related_products(product.id, top_n=limit)
    
    results = []
    for pid, score in collab_items:
        try:
            p = Product.objects.select_related('category', 'brand').get(id=pid, is_active=True)
            results.append({
                'product': p,
                'score': round(score, 3),
                'algorithm': 'COLLABORATIVE',
                'explanation': "Customers who viewed this also frequently interacted with this"
            })
        except Product.DoesNotExist:
            continue

    # Fallback if sparse interaction data exists
    if len(results) < limit:
        existing_ids = [r['product'].id for r in results] + [product.id]
        trending_fillers = Product.objects.filter(is_active=True).exclude(id__in=existing_ids).order_by('-view_count')[:limit - len(results)]
        for p in trending_fillers:
            results.append({
                'product': p,
                'score': 0.4,
                'algorithm': 'TRENDING',
                'explanation': "Customers also frequently browsed this trending item"
            })

    return results


def get_trending_products(limit=8):
    """Returns top trending products based on views and activity."""
    return Product.objects.filter(is_active=True, stock__gt=0).order_by('-view_count', '-rating_avg')[:limit]


def get_recently_viewed(user=None, session_key=None, limit=6):
    """Fetches unique recently viewed products by this user/session."""
    query = UserActivity.objects.filter(activity_type='VIEW', product__isnull=False)
    if user and user.is_authenticated:
        query = query.filter(user=user)
    elif session_key:
        query = query.filter(session_key=session_key)
    else:
        return []

    recent_activities = query.order_by('-created_at')[:20]
    seen_ids = set()
    recent_products = []
    for act in recent_activities:
        if act.product_id not in seen_ids and act.product.is_active:
            seen_ids.add(act.product_id)
            recent_products.append(act.product)
            if len(recent_products) >= limit:
                break
    return recent_products


def retrain_all_engines():
    """Retrains both Content-Based and Collaborative Filtering models."""
    cb_status = content_recommender.train()
    cf_status = collaborative_recommender.train()
    return {'content_based': cb_status, 'collaborative': cf_status}
