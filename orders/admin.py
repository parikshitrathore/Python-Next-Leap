from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price_at_purchase']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_price', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email']
    list_filter = ['status']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'user', 'total_price', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    #  This means when you open an Order in admin, you'll see the order details plus all its items in a table below — without needing to go to a separate page. That's an inline — it embeds a related model inside the parent's detail page.

