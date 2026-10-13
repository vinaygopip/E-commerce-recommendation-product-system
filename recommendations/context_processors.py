from .models import Wishlist

def wishlist_context(request):
    wishlist_count = 0
    wishlist_product_ids = set()

    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_product_ids = set(wishlist.items.values_list('product_id', flat=True))
            wishlist_count = len(wishlist_product_ids)

    return {
        'navbar_wishlist_count': wishlist_count,
        'user_wishlist_ids': wishlist_product_ids,
    }
