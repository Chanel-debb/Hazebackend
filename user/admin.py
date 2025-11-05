from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'created_at', 'updated_at', )
    search_fields = ('email', 'first_name', 'last_name', 'phone_number', 'other_names', 'role')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_verified', 'created_at', 'updated_at',)
    ordering = ('-created_at', 'updated_at',)


admin.site.register(User, UserAdmin)