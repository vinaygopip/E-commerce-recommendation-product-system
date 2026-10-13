from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from products.models import Product
from orders.models import OrderItem
from recommendations.engine import log_user_activity

@login_required
def add_review_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if request.method == 'POST':
        # Check if already reviewed
        existing_review = Review.objects.filter(product=product, user=request.user).first()
        form = ReviewForm(request.POST, instance=existing_review) if existing_review else ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            
            # Check verified purchase
            has_bought = OrderItem.objects.filter(order__user=request.user, product=product).exists()
            review.is_verified_purchase = has_bought
            review.save()

            # Log RATING activity to train recommendation model
            log_user_activity(
                user=request.user,
                session_key=request.session.session_key,
                product=product,
                activity_type='RATING',
                rating_value=review.rating
            )

            messages.success(request, f"Your review for {product.name} has been published!")
        else:
            messages.error(request, "Failed to submit review. Please check the form inputs.")

    return redirect('product_detail', slug=product.slug)


@login_required
def delete_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    slug = review.product.slug
    review.delete()
    messages.info(request, "Your review has been removed.")
    return redirect('product_detail', slug=slug)
