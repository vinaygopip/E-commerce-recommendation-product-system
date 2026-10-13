"""
Hybrid Recommendation Engine
Combines:
  1. Content-Based TF-IDF Similarity (40%)
  2. User Behavior & Category Affinity (30%)
  3. Collaborative Filtering Co-occurrence (20%)
  4. Global Popularity / Rating (10%)
Handles Cold-Start gracefully with trending & top-rated fallback.
"""

from products.models import Product, Category
from recommendations.models import UserActivity
from .content_based import content_recommender
from .collaborative import collaborative_recommender
from django.db.models import Count, Avg, Q
import random

class HybridRecommender:
    def __init__(self, w_content=0.40, w_user_affinity=0.30, w_collab=0.20, w_popularity=0.10):
        self.w_content = w_content
        self.w_user_affinity = w_user_affinity
        self.w_collab = w_collab
        self.w_popularity = w_popularity

    def get_cold_start_recommendations(self, limit=8, preferred_category_ids=None):
        """Fallback recommendation strategy for brand-new users or guest visitors."""
        query = Product.objects.filter(is_active=True, stock__gt=0)
        if preferred_category_ids:
            query = query.filter(category_id__in=preferred_category_ids)

        # Mix trending (views) and top-rated
        popular_products = query.order_by('-view_count', '-rating_avg')[:limit * 2]
        selected = list(popular_products)
        if len(selected) > limit:
            selected = random.sample(selected, limit)

        results = []
        for p in selected:
            results.append({
                'product': p,
                'score': round(float(p.rating_avg) / 5.0, 2),
                'algorithm': 'COLD_START',
                'explanation': f"Popular in {p.category.name} with ⭐ {p.rating_avg} rating"
            })
        return results

    def recommend(self, user=None, session_key=None, limit=8):
        """
        Generates personalized hybrid recommendations for a given user or guest session.
        Returns a list of dicts: [{'product': Product, 'score': float, 'algorithm': str, 'explanation': str}]
        """
        # 1. Fetch user recent interactions
        activities_query = UserActivity.objects.filter(product__isnull=False)
        if user and user.is_authenticated:
            user_key = f"u_{user.id}"
            user_activities = activities_query.filter(user=user).select_related('product', 'product__category')[:30]
        elif session_key:
            user_key = f"s_{session_key}"
            user_activities = activities_query.filter(session_key=session_key).select_related('product', 'product__category')[:30]
        else:
            return self.get_cold_start_recommendations(limit=limit)

        if not user_activities.exists():
            # Check if user profile has preferred categories
            pref_cats = []
            if user and user.is_authenticated and hasattr(user, 'profile') and user.profile.preferred_categories:
                pref_slugs = [s.strip() for s in user.profile.preferred_categories.split(',') if s.strip()]
                pref_cats = list(Category.objects.filter(slug__in=pref_slugs).values_list('id', flat=True))
            return self.get_cold_start_recommendations(limit=limit, preferred_category_ids=pref_cats)

        # 2. Extract user interaction profile
        interacted_product_ids = set()
        category_weights = {}
        last_viewed_product = None

        for act in user_activities:
            pid = act.product_id
            interacted_product_ids.add(pid)
            weight = act.score_weight
            
            # Category affinity
            cat_id = act.product.category_id
            category_weights[cat_id] = category_weights.get(cat_id, 0.0) + weight

            if not last_viewed_product and act.activity_type in ['VIEW', 'CLICK']:
                last_viewed_product = act.product

        # Candidate pool: active products in stock not already heavily purchased/added
        candidates = Product.objects.filter(is_active=True, stock__gt=0).exclude(id__in=interacted_product_ids)
        if not candidates.exists():
            candidates = Product.objects.filter(is_active=True, stock__gt=0)

        candidate_list = list(candidates.select_related('category', 'brand')[:100])
        candidate_ids = [p.id for p in candidate_list]

        if not candidate_ids:
            return self.get_cold_start_recommendations(limit=limit)

        # Normalize category affinity
        max_cat_weight = max(category_weights.values()) if category_weights else 1.0

        # 3. Compute Component Scores
        # A. Content-based similarity from interacted products
        content_scores = content_recommender.get_content_scores_for_products(list(interacted_product_ids), candidate_ids)

        # B. Collaborative scores from interaction matrix
        collab_scores = collaborative_recommender.get_user_collaborative_scores(user_key, candidate_ids)

        # C. Max views across candidates for popularity normalization
        max_views = max([p.view_count for p in candidate_list] + [1])

        # 4. Calculate Weighted Hybrid Score
        scored_candidates = []
        for p in candidate_list:
            c_score = content_scores.get(p.id, 0.0)
            cb_score = collab_scores.get(p.id, 0.0)
            
            # User category affinity score (0.0 to 1.0)
            cat_weight = category_weights.get(p.category_id, 0.0)
            affinity_score = cat_weight / max_cat_weight if max_cat_weight > 0 else 0.0

            # Popularity score
            pop_score = ((p.view_count / max_views) * 0.5) + ((float(p.rating_avg) / 5.0) * 0.5)

            # Hybrid score
            hybrid_score = (
                (self.w_content * c_score) +
                (self.w_user_affinity * affinity_score) +
                (self.w_collab * cb_score) +
                (self.w_popularity * pop_score)
            )

            # Determine human explanation
            if c_score > 0.35 and last_viewed_product:
                explanation = f"Because you viewed {last_viewed_product.name[:35]}"
            elif affinity_score > 0.4:
                explanation = f"Matches your interest in {p.category.name}"
            elif cb_score > 0.2:
                explanation = "Frequently shopped by customers with similar taste"
            else:
                explanation = f"Trending pick in {p.category.name} (⭐ {p.rating_avg})"

            scored_candidates.append({
                'product': p,
                'score': round(hybrid_score, 4),
                'content_score': round(c_score, 3),
                'collab_score': round(cb_score, 3),
                'affinity_score': round(affinity_score, 3),
                'algorithm': 'HYBRID',
                'explanation': explanation
            })

        # Sort descending by hybrid score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates[:limit]


hybrid_recommender = HybridRecommender()
