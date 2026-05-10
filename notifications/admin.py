from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']
    list_filter = ['is_read']
    ordering = ['-created_at']
    readonly_fields = ['user', 'message', 'created_at']
