from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('thank-you/<str:order_number>/', views.thank_you, name='thank_you'),
    path('history/', views.order_history, name='order_history'),
    path('track/', views.track_order, name='track_order'),
    path('<str:order_number>/', views.order_detail, name='order_detail'),
]
