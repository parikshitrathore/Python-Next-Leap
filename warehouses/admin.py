from django.contrib import admin

from .models import Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'capacity', 'is_active', 'created_at']
    search_fields = ['name', 'city', 'state']
    list_filter = ['is_active', 'state']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
