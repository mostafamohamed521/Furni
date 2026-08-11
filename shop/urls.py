from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop_list, name='shop_list'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('wishlist/toggle/<slug:slug>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
