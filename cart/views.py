from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem
from products.models import Product
from recommendations.engine import log_user_activity

def get_or_create_cart(request):
    """Helper function to retrieve or create cart for authenticated user or anonymous session."""
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_detail_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'product__category').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': cart.get_total_regular_price(),
        'savings': cart.get_total_savings(),
        'total': cart.get_total_price(),
    }
    return render(request, 'cart/cart_detail.html', context)


def cart_add_view(request, product_id):
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    quantity = int(request.POST.get('quantity', 1)) if request.method == 'POST' else 1
    if quantity <= 0:
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    # Log CART_ADD activity to strengthen recommendation models
    log_user_activity(
        user=request.user,
        session_key=request.session.session_key,
        product=product,
        activity_type='CART_ADD'
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'message': f"Added {product.name} to cart.",
            'cart_count': cart.get_total_items(),
            'cart_total': float(cart.get_total_price())
        })

    messages.success(request, f"Added '{product.name}' to your cart.")
    return redirect(request.META.get('HTTP_REFERER', 'cart_detail'))


def cart_update_view(request, product_id):
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    action = request.POST.get('action') or request.GET.get('action')
    if action == 'increment':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrement':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'item_quantity': cart_item.quantity if cart_item.id else 0,
            'item_subtotal': float(cart_item.get_subtotal()) if cart_item.id else 0,
            'cart_count': cart.get_total_items(),
            'cart_total': float(cart.get_total_price())
        })

    return redirect('cart_detail')


def cart_remove_view(request, product_id):
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item:
        cart_item.delete()
        messages.info(request, f"Removed '{product.name}' from your cart.")
    return redirect('cart_detail')
