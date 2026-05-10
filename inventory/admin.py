from django.contrib import admin

from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity_available', 'reserved_quantity', 'updated_at']
    search_fields = ['product__name', 'warehouse__name']
    list_filter = ['warehouse']
    ordering = ['-updated_at']
    # reserved_quantity is system-managed (auto-updated on order placement/cancellation)
    readonly_fields = ['reserved_quantity', 'updated_at']
