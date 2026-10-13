from django.urls import path
from . import views

urlpatterns = [
    path('analytics/', views.dashboard_view, name='admin_dashboard'),
    path('analytics/retrain/', views.retrain_models_view, name='admin_retrain_models'),
    path('delete/user/<int:user_id>/', views.delete_user_view, name='admin_delete_user'),
    path('delete/product/<int:product_id>/', views.delete_product_view, name='admin_delete_product'),
    path('delete/order/<int:order_id>/', views.delete_order_view, name='admin_delete_order'),
]

