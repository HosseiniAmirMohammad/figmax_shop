from django.contrib import admin
from .models import Order, OrderItem, Cart

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_editable = ['status']
    list_filter = ['status']
    search_fields = ['user__username']
    inlines = [OrderItemInline]
    list_per_page = 20

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'created_at']
    list_per_page = 20