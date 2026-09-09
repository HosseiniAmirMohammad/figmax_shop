# apps/shop/urls.py

from django.urls import path, re_path
from . import views
from . import views_cart

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('about/', views.about, name='about'),
    re_path(r'^product/(?P<product_slug>[^/]+)/$', views.product_detail, name='product_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # BUY CARD - سبد خرید
    path('cart/', views_cart.cart_view, name='cart'),
    path('cart/add/', views_cart.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views_cart.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views_cart.remove_from_cart, name='remove_from_cart'),
    path('cart/count/', views_cart.cart_count, name='cart_count'),
    
    # CHECKOUT - تسویه حساب
    path('checkout/', views_cart.checkout, name='checkout'),
    path('orders/', views_cart.orders_list, name='orders_list'),
    path('order/<int:order_id>/', views_cart.order_detail, name='order_detail'),
]