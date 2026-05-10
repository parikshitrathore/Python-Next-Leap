from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
#  @admin.register(User) — tells Django: "show this model in the admin panel"
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'name', 'city', 'state', 'is_staff', 'is_active', 'created_at']
    #  which columns appear in the list view table
    search_fields = ['username', 'email', 'name', 'city']
    # search_fields — which fields the search bar searches through
    list_filter = ['is_staff', 'is_active', 'state', 'city']
    # list_filter — sidebar filters on the right side of the list
    ordering = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {
            'fields': ('name', 'date_of_birth', 'address', 'state', 'city')
        }),
    )
