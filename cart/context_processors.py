from .models import Cart

def cart_context(request):
    cart_items_count = 0
    cart_total_price = 0
    cart = None

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()

    if cart:
        cart_items_count = cart.get_total_items()
        cart_total_price = cart.get_total_price()

    return {
        'navbar_cart_count': cart_items_count,
        'navbar_cart_total': cart_total_price,
    }
