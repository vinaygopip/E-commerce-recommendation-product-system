from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add_view, name='cart_add'),
    path('update/<int:product_id>/', views.cart_update_view, name='cart_update'),
    path('remove/<int:product_id>/', views.cart_remove_view, name='cart_remove'),
]
