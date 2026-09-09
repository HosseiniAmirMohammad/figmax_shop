# apps/accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('orders/', views.orders_view, name='orders'),
    path('cart/', views.cart_view, name='cart'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
]