from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('store/', views.home_view, name='home'),
    path('welcome/', views.landing_view, name='welcome'),
    path('products/', views.product_list_view, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list_view, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
]
