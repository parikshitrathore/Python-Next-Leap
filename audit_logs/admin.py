from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['order', 'old_status', 'new_status', 'changed_at']
    search_fields = ['order__order_number']
    list_filter = ['old_status', 'new_status']
    ordering = ['-changed_at']
    readonly_fields = ['order', 'old_status', 'new_status', 'changed_at']
