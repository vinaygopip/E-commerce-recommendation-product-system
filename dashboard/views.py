from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .analytics import get_dashboard_metrics
from recommendations.engine import retrain_all_engines
from recommendations.content_based import content_recommender
from recommendations.collaborative import collaborative_recommender

def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin_or_staff, login_url='login')
def dashboard_view(request):
    """
    Admin and Machine Learning Analytics Dashboard.
    Renders business KPIs, ML funnel, activity breakdown, and Chart.js graphs.
    """
    metrics = get_dashboard_metrics()
    
    # ML model diagnostics
    ml_status = {
        'content_based_trained': content_recommender.tfidf_matrix is not None,
        'content_products_indexed': len(content_recommender.product_ids) if content_recommender.product_ids else 0,
        'collab_matrix_trained': collaborative_recommender.item_sim_df is not None,
        'collab_users_count': collaborative_recommender.user_item_matrix.shape[0] if collaborative_recommender.user_item_matrix is not None else 0,
        'collab_items_count': collaborative_recommender.user_item_matrix.shape[1] if collaborative_recommender.user_item_matrix is not None else 0,
    }

    context = {
        'metrics': metrics,
        'ml_status': ml_status,
    }
    return render(request, 'dashboard/dashboard.html', context)


@user_passes_test(is_admin_or_staff, login_url='login')
def delete_user_view(request, user_id):
    """
    Deletes a registered user from the database.
    """
    if request.method == 'POST':
        from django.contrib.auth.models import User
        try:
            target_user = User.objects.get(id=user_id)
            if target_user.id == request.user.id:
                messages.error(request, "Security protection: You cannot delete your own currently logged-in account.")
            else:
                username = target_user.username
                target_user.delete()
                messages.success(request, f"User account '{username}' (ID #{user_id}) has been deleted.")
        except User.DoesNotExist:
            messages.error(request, "User account not found.")
    return redirect('admin_dashboard')


@user_passes_test(is_admin_or_staff, login_url='login')
def delete_product_view(request, product_id):
    """
    Deletes a product from the active catalog and triggers recommendation cache update.
    """
    if request.method == 'POST':
        from products.models import Product
        try:
            product = Product.objects.get(id=product_id)
            product_name = product.name
            product.delete()
            messages.success(request, f"Product '{product_name}' (ID #{product_id}) has been removed from catalog.")
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
    return redirect('admin_dashboard')


@user_passes_test(is_admin_or_staff, login_url='login')
def delete_order_view(request, order_id):
    """
    Deletes a customer order record.
    """
    if request.method == 'POST':
        from orders.models import Order
        try:
            order = Order.objects.get(id=order_id)
            order_num = order.order_number
            order.delete()
            messages.success(request, f"Order '{order_num}' (ID #{order_id}) has been deleted.")
        except Order.DoesNotExist:
            messages.error(request, "Order record not found.")
    return redirect('admin_dashboard')


@user_passes_test(is_admin_or_staff, login_url='login')
def retrain_models_view(request):
    """
    Triggers on-demand training of TF-IDF Content-Based and Collaborative Filtering models.
    """
    result = retrain_all_engines()
    messages.success(
        request,
        f"Machine Learning models successfully retrained! (Content-Based: {'Success' if result['content_based'] else 'No Data'}, "
        f"Collaborative: {'Success' if result['collaborative'] else 'Insufficient Interactions'})"
    )
    return redirect('admin_dashboard')


