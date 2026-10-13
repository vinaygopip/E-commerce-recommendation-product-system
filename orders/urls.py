from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('my-orders/', views.order_list_view, name='order_list'),
    path('order/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('invoice/<str:order_number>/', views.order_invoice_pdf_view, name='order_invoice'),
]
