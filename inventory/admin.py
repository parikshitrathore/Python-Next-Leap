from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity_available', 'reserved_quantity', 'updated_at')
    list_filter = ('warehouse', 'product')
    search_fields = ('product__name', 'product__sku', 'warehouse__name')
    readonly_fields = ('updated_at',)
