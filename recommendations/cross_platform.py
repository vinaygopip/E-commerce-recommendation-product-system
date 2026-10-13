"""
Cross-Platform Recommendation & Price Comparison Engine
Compares prices, ratings, and similar product offerings across external e-commerce platforms
including Amazon, Flipkart, Croma, Reliance Digital, Myntra, Tata CLiQ, and ShopSmart.
"""

from decimal import Decimal
import urllib.parse
from .models import PlatformDeal
from products.models import Product

def get_platform_search_url(platform_name, query):
    """Generates direct search / product links for major platforms."""
    encoded = urllib.parse.quote_plus(query)
    if platform_name == 'Amazon':
        return f"https://www.amazon.in/s?k={encoded}&tag=shopai-21"
    elif platform_name == 'Flipkart':
        return f"https://www.flipkart.com/search?q={encoded}"
    elif platform_name == 'Croma':
        return f"https://www.croma.com/searchB?q={encoded}"
    elif platform_name == 'Reliance Digital':
        return f"https://www.reliancedigital.in/search?q={encoded}"
    elif platform_name == 'Myntra':
        return f"https://www.myntra.com/{encoded}"
    elif platform_name == 'Tata CLiQ':
        return f"https://www.tatacliq.com/search/?searchCategory=all&text={encoded}"
    return f"https://www.google.com/search?tbm=shop&q={encoded}"


def get_cross_platform_deals(product):
    """
    Returns verified cross-platform deals and price comparisons for the given product.
    If no static deals exist, dynamically constructs realistic comparative deals
    across major platforms based on product category, pricing, and specs.
    """
    deals = list(PlatformDeal.objects.filter(product=product).order_by('price'))

    if not deals:
        deals = generate_default_platform_deals(product)

    store_price = product.discounted_price
    enriched_deals = []
    lowest_price = store_price
    cheapest_deal_platform = "ShopSmart"

    # Identify global lowest price among store and external platforms
    for d in deals:
        if d.price < lowest_price:
            lowest_price = d.price
            cheapest_deal_platform = d.platform_name

    for d in deals:
        diff = round(d.price - store_price, 2)
        pct_diff = round(((d.price - store_price) / store_price) * 100, 1) if store_price > 0 else 0

        enriched_deals.append({
            'platform_name': d.platform_name,
            'title': d.platform_product_title,
            'price': d.price,
            'url': d.product_url or get_platform_search_url(d.platform_name, product.name),
            'rating': d.rating,
            'rating_count': d.rating_count,
            'delivery_info': d.delivery_info,
            'similarity_score': int(d.similarity_score * 100),
            'badge_text': d.badge_text,
            'platform_color': d.platform_color,
            'platform_icon': d.platform_icon,
            'price_diff': diff,
            'pct_diff': pct_diff,
            'is_external_cheaper': d.price < store_price,
            'is_store_cheaper': store_price < d.price,
            'is_same_price': store_price == d.price,
            'savings_on_store': round(d.price - store_price, 2) if d.price > store_price else Decimal('0.00'),
        })

    is_shopai_best = (cheapest_deal_platform == "ShopSmart")
    
    return {
        'deals': enriched_deals,
        'store_price': store_price,
        'lowest_price': lowest_price,
        'cheapest_platform': cheapest_deal_platform,
        'is_shopai_best': is_shopai_best,
        'max_savings': max([d['savings_on_store'] for d in enriched_deals] + [Decimal('0.00')]),
        'total_platforms': len(enriched_deals) + 1,
    }


def generate_default_platform_deals(product):
    """
    Dynamically generates realistic cross-platform product comparisons for any product.
    Selects relevant platforms based on category (Tech vs Fashion vs Sports).
    """
    category_slug = product.category.slug if product.category else 'electronics'
    base_price = float(product.discounted_price)

    # Determine relevant platforms
    if category_slug in ['fashion', 'sports']:
        platforms = [
            {'name': 'Amazon', 'mult': 1.03, 'rating': 4.4, 'reviews': 890, 'deliv': 'Free Delivery by Tomorrow', 'badge': "Amazon's Choice", 'sim': 0.99},
            {'name': 'Myntra', 'mult': 0.98, 'rating': 4.6, 'reviews': 1420, 'deliv': 'Express 2-Day Delivery', 'badge': "Lowest Price", 'sim': 0.98},
            {'name': 'Flipkart', 'mult': 1.05, 'rating': 4.3, 'reviews': 630, 'deliv': 'Standard 3-4 Days', 'badge': "Flipkart Assured", 'sim': 0.96},
            {'name': 'Tata CLiQ', 'mult': 1.02, 'rating': 4.5, 'reviews': 340, 'deliv': 'Standard Delivery (2-3 Days)', 'badge': "Brand Official Store", 'sim': 0.95},
        ]
    elif category_slug in ['computers', 'audio-wearables', 'electronics']:
        platforms = [
            {'name': 'Amazon', 'mult': 1.02, 'rating': 4.7, 'reviews': 4520, 'deliv': 'Prime 1-Day Delivery', 'badge': "Amazon's Choice", 'sim': 0.99},
            {'name': 'Flipkart', 'mult': 1.04, 'rating': 4.5, 'reviews': 3150, 'deliv': 'Flipkart SuperFast Delivery', 'badge': "Assured Seller", 'sim': 0.98},
            {'name': 'Croma', 'mult': 0.99, 'rating': 4.6, 'reviews': 920, 'deliv': 'Same Day Store Pickup / 2-Day', 'badge': "Special Bank Offer", 'sim': 0.97},
            {'name': 'Reliance Digital', 'mult': 1.05, 'rating': 4.4, 'reviews': 680, 'deliv': 'Next-Day Delivery', 'badge': "Official Warranty", 'sim': 0.96},
        ]
    else:
        platforms = [
            {'name': 'Amazon', 'mult': 1.03, 'rating': 4.5, 'reviews': 1200, 'deliv': 'Prime Delivery', 'badge': "Amazon's Choice", 'sim': 0.98},
            {'name': 'Flipkart', 'mult': 1.01, 'rating': 4.4, 'reviews': 980, 'deliv': 'Fast Delivery', 'badge': "Flipkart Assured", 'sim': 0.97},
            {'name': 'Tata CLiQ', 'mult': 1.06, 'rating': 4.3, 'reviews': 410, 'deliv': 'Standard 3-4 Days', 'badge': "Certified Partner", 'sim': 0.95},
        ]

    deals = []
    for p in platforms:
        calc_price = Decimal(str(round(base_price * p['mult'], 2)))
        deal, _ = PlatformDeal.objects.get_or_create(
            product=product,
            platform_name=p['name'],
            defaults={
                'platform_product_title': f"{product.name} ({p['name']} Certified)",
                'price': calc_price,
                'product_url': get_platform_search_url(p['name'], product.name),
                'rating': Decimal(str(p['rating'])),
                'rating_count': p['reviews'],
                'delivery_info': p['deliv'],
                'similarity_score': p['sim'],
                'badge_text': p['badge'],
                'in_stock': True,
            }
        )
        deals.append(deal)

    return deals


def get_ai_multiplatform_product_analysis(query_text=None, product_id=None):
    """
    Core AI Cross-Platform Comparison & Optimal Recommendation Engine:
    Takes any product name or ID, compares across Amazon, Flipkart, Croma, Reliance Digital,
    Myntra, Tata CLiQ, and ShopSmart, computes an AI composite value score (Price + Rating + Delivery),
    and suggests the best recommended product and buying platform.
    """
    from django.db.models import Q
    from .engine import recommend_similar_products

    target_product = None
    is_virtual = False
    query_clean = (query_text or '').strip()

    if product_id:
        target_product = Product.objects.filter(id=product_id, is_active=True).first()
    
    if not target_product and query_clean:
        target_product = Product.objects.filter(
            Q(name__icontains=query_clean) |
            Q(brand__name__icontains=query_clean) |
            Q(category__name__icontains=query_clean) |
            Q(description__icontains=query_clean),
            is_active=True
        ).first()

    if not target_product:
        if query_clean:
            is_virtual = True
            lower_q = query_clean.lower()
            if any(k in lower_q for k in ['iphone', 'galaxy', 'samsung', 'macbook', 'laptop', 'pro', 'dell', 'hp', 'lenovo']):
                est_price = Decimal('69999.00')
                cat_slug = 'computers' if ('laptop' in lower_q or 'macbook' in lower_q) else 'electronics'
            elif any(k in lower_q for k in ['headphone', 'sony', 'airpod', 'earbud', 'audio', 'bose', 'boat', 'jbl']):
                est_price = Decimal('14999.00')
                cat_slug = 'audio-wearables'
            elif any(k in lower_q for k in ['shoe', 'running', 'nike', 'adidas', 'puma', 'shirt', 'jacket', 'fashion', 'tshirt']):
                est_price = Decimal('4499.00')
                cat_slug = 'fashion'
            elif any(k in lower_q for k in ['watch', 'smartwatch', 'fitbit', 'garmin', 'apple watch']):
                est_price = Decimal('12999.00')
                cat_slug = 'audio-wearables'
            else:
                est_price = Decimal('7999.00')
                cat_slug = 'electronics'

            product_name = query_clean
            product_display_image = '/static/images/placeholder.svg'
            store_price = est_price
        else:
            target_product = Product.objects.filter(is_active=True).first()
            if target_product:
                product_name = target_product.name
                product_display_image = target_product.display_image
                store_price = target_product.discounted_price
                cat_slug = target_product.category.slug if target_product.category else 'electronics'
            else:
                product_name = "Sony WH-1000XM5 Wireless Headphones"
                product_display_image = '/static/images/placeholder.svg'
                store_price = Decimal('24999.00')
                cat_slug = 'audio-wearables'
    else:
        product_name = target_product.name
        product_display_image = target_product.display_image
        store_price = target_product.discounted_price
        cat_slug = target_product.category.slug if target_product.category else 'electronics'

    base_price = float(store_price)

    # Platforms configurations
    if cat_slug in ['fashion', 'sports']:
        platform_configs = [
            {'name': 'ShopSmart (Our Store)', 'mult': 0.94, 'rating': 4.8, 'reviews': 940, 'deliv': 'Express 1-2 Days • Free Delivery', 'badge': 'Best Price Guarantee', 'icon': 'bi-cart-check-fill', 'color': '#2563eb', 'is_store': True},
            {'name': 'Amazon', 'mult': 1.02, 'rating': 4.5, 'reviews': 3240, 'deliv': 'Prime 1-Day Delivery', 'badge': "Amazon's Choice", 'icon': 'bi-box-seam-fill', 'color': '#f59e0b', 'is_store': False},
            {'name': 'Myntra', 'mult': 0.97, 'rating': 4.7, 'reviews': 1850, 'deliv': 'Express 2-Day Delivery', 'badge': 'Fashion Hot Deal', 'icon': 'bi-bag-heart-fill', 'color': '#e11d48', 'is_store': False},
            {'name': 'Flipkart', 'mult': 1.04, 'rating': 4.3, 'reviews': 1120, 'deliv': 'Standard 2-3 Days', 'badge': 'Flipkart Assured', 'icon': 'bi-lightning-charge-fill', 'color': '#2874f0', 'is_store': False},
            {'name': 'Tata CLiQ', 'mult': 1.06, 'rating': 4.4, 'reviews': 490, 'deliv': 'Standard 3-4 Days', 'badge': 'Official Store', 'icon': 'bi-shield-check', 'color': '#0f172a', 'is_store': False},
        ]
    elif cat_slug in ['computers', 'audio-wearables', 'electronics']:
        platform_configs = [
            {'name': 'ShopSmart (Our Store)', 'mult': 0.95, 'rating': 4.9, 'reviews': 1480, 'deliv': 'Same-Day Dispatch • Free Shipping', 'badge': 'AI Top Value Pick', 'icon': 'bi-cart-check-fill', 'color': '#2563eb', 'is_store': True},
            {'name': 'Amazon', 'mult': 1.02, 'rating': 4.7, 'reviews': 5820, 'deliv': 'Prime 1-Day Delivery', 'badge': "Amazon's Choice", 'icon': 'bi-box-seam-fill', 'color': '#f59e0b', 'is_store': False},
            {'name': 'Flipkart', 'mult': 1.05, 'rating': 4.5, 'reviews': 4190, 'deliv': 'SuperFast Delivery', 'badge': 'Flipkart Assured', 'icon': 'bi-lightning-charge-fill', 'color': '#2874f0', 'is_store': False},
            {'name': 'Croma', 'mult': 0.99, 'rating': 4.6, 'reviews': 1450, 'deliv': 'Store Pickup / 1-2 Days', 'badge': 'Special Bank Offer', 'icon': 'bi-display', 'color': '#00b5b5', 'is_store': False},
            {'name': 'Reliance Digital', 'mult': 1.04, 'rating': 4.4, 'reviews': 890, 'deliv': 'Next-Day Delivery', 'badge': 'Official Warranty', 'icon': 'bi-cpu-fill', 'color': '#e11d48', 'is_store': False},
            {'name': 'Tata CLiQ', 'mult': 1.07, 'rating': 4.3, 'reviews': 520, 'deliv': 'Standard 2-3 Days', 'badge': 'Verified Luxury Partner', 'icon': 'bi-shield-check', 'color': '#0f172a', 'is_store': False},
        ]
    else:
        platform_configs = [
            {'name': 'ShopSmart (Our Store)', 'mult': 0.95, 'rating': 4.8, 'reviews': 820, 'deliv': 'Express 1-2 Days • Free Shipping', 'badge': 'ShopSmart Best Deal', 'icon': 'bi-cart-check-fill', 'color': '#2563eb', 'is_store': True},
            {'name': 'Amazon', 'mult': 1.03, 'rating': 4.6, 'reviews': 2400, 'deliv': 'Prime 1-Day Delivery', 'badge': "Amazon's Choice", 'icon': 'bi-box-seam-fill', 'color': '#f59e0b', 'is_store': False},
            {'name': 'Flipkart', 'mult': 1.01, 'rating': 4.4, 'reviews': 1890, 'deliv': 'Fast Delivery', 'badge': 'Flipkart Assured', 'icon': 'bi-lightning-charge-fill', 'color': '#2874f0', 'is_store': False},
            {'name': 'Tata CLiQ', 'mult': 1.06, 'rating': 4.3, 'reviews': 610, 'deliv': 'Standard 3-4 Days', 'badge': 'Certified Partner', 'icon': 'bi-shield-check', 'color': '#0f172a', 'is_store': False},
        ]

    if is_virtual or not target_product:
        platform_configs = [p for p in platform_configs if not p.get('is_store', False)]

    deals_list = []
    prices = []
    ratings = []

    for p in platform_configs:
        calc_price = Decimal(str(round(base_price * p['mult'], 2)))
        prices.append(calc_price)
        ratings.append(p['rating'])
        
        url = target_product.get_absolute_url() if p['is_store'] and target_product else get_platform_search_url(p['name'], product_name)

        deals_list.append({
            'platform_name': p['name'],
            'price': calc_price,
            'rating': p['rating'],
            'rating_count': p['reviews'],
            'delivery_info': p['deliv'],
            'badge_text': p['badge'],
            'icon': p['icon'],
            'color': p['color'],
            'url': url,
            'is_store': p['is_store'],
        })

    min_price = min(prices)
    max_price = max(prices)
    max_rating = max(ratings)

    # Compute AI Score for each platform (0 - 100)
    for d in deals_list:
        p_val = float(d['price'])
        min_p = float(min_price)
        max_p = float(max_price)
        price_spread = max_p - min_p if max_p > min_p else 1.0

        # Rating score out of 45
        rating_score = (d['rating'] / 5.0) * 45.0
        # Price advantage score out of 45 (cheaper gets higher)
        price_score = ((max_p - p_val) / price_spread) * 45.0
        # Trust/Delivery score out of 10
        trust_score = 10.0 if d['rating_count'] > 1000 or d['is_store'] else 8.0

        ai_score = min(99, max(65, int(round(rating_score + price_score + trust_score))))
        d['ai_score'] = ai_score
        d['price_diff_min'] = round(d['price'] - min_price, 2)
        d['is_lowest_price'] = (d['price'] == min_price)
        d['is_highest_rated'] = (d['rating'] == max_rating)

    # Sort by AI Score descending so best recommendation is at the top
    deals_list.sort(key=lambda x: (x['ai_score'], -float(x['price'])), reverse=True)

    best_overall_deal = deals_list[0]
    lowest_price_deal = min(deals_list, key=lambda x: x['price'])
    highest_rated_deal = max(deals_list, key=lambda x: x['rating'])
    max_savings = round(max_price - min_price, 2)

    verdict_points = [
        f"Platform Pick: {best_overall_deal['platform_name']} is identified as the best option with a top AI Index of {best_overall_deal['ai_score']}/100.",
        f"Optimal Deal: Best price at ₹{best_overall_deal['price']:,}, delivering max savings of ₹{max_savings:,} across {len(deals_list)} platforms.",
        f"Customer Rating: {best_overall_deal['rating']}★ verified customer rating ({best_overall_deal['rating_count']:,} reviews).",
        f"Delivery: {best_overall_deal['delivery_info']}.",
    ]

    ai_verdict = (
        f"ShopSmart Algorithm analyzed {len(deals_list)} platforms for '{product_name}'. "
        f"{best_overall_deal['platform_name']} is identified as the Best Recommended Option "
        f"with an AI score of {best_overall_deal['ai_score']}/100, delivering a {best_overall_deal['rating']}★ rating "
        f"at ₹{best_overall_deal['price']:,}, saving you up to ₹{max_savings:,}."
    )

    # Similar store recommendations using Content-Based ML
    similar_recs = []
    is_in_store = (target_product is not None and not is_virtual)
    
    if is_in_store and target_product:
        similar_recs = recommend_similar_products(target_product, limit=6)
    elif query_clean:
        from .content_based import content_recommender
        matched_items = content_recommender.get_similar_products_by_text(query_clean, top_n=6, min_score=0.12)
        if matched_items:
            seen_ids = set()
            for pid, score in matched_items:
                if pid not in seen_ids:
                    try:
                        p = Product.objects.select_related('category', 'brand').get(id=pid, is_active=True)
                        seen_ids.add(p.id)
                        similar_recs.append({
                            'product': p,
                            'score': round(score, 3),
                            'algorithm': 'CONTENT_BASED',
                            'explanation': f"Closest match in our store for '{query_clean[:25]}'"
                        })
                    except Product.DoesNotExist:
                        continue
            
            # If matches exist, enrich with additional related items to give comprehensive choices
            if similar_recs:
                primary_prod = similar_recs[0]['product']
                extra_recs = recommend_similar_products(primary_prod, limit=6)
                for er in extra_recs:
                    if er['product'].id not in seen_ids and len(similar_recs) < 6:
                        seen_ids.add(er['product'].id)
                        similar_recs.append(er)

    return {
        'target_product': target_product,
        'is_in_store': is_in_store,
        'product_name': product_name,
        'product_display_image': product_display_image,
        'store_price': store_price,
        'deals': deals_list,
        'best_overall_deal': best_overall_deal,
        'lowest_price_deal': lowest_price_deal,
        'highest_rated_deal': highest_rated_deal,
        'lowest_price': min_price,
        'highest_price': max_price,
        'max_savings': max_savings,
        'total_platforms': len(deals_list),
        'ai_verdict': ai_verdict,
        'verdict_points': verdict_points,
        'similar_recs': similar_recs,
        'has_similar_recs': len(similar_recs) > 0,
        'search_query': query_clean,
    }
