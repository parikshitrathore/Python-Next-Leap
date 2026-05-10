from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'city', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('name', 'date_of_birth', 'address', 'state', 'city')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('name', 'date_of_birth', 'address', 'state', 'city')}),
    )
    search_fields = ('username', 'email', 'name', 'city')