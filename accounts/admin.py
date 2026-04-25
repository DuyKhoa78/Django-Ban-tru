from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StaffUser


@admin.register(StaffUser)
class StaffUserAdmin(UserAdmin):
    """Admin cho StaffUser – hiển thị thêm cột role, fullname."""

    list_display  = ('username', 'fullname', 'role', 'position', 'is_active', 'is_superuser')
    list_filter   = ('role', 'is_active', 'is_superuser')
    search_fields = ('username', 'fullname', 'position')
    ordering      = ('role', 'username')

    # Thêm fieldsets tùy chỉnh để hiển thị role & fullname khi sửa user
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {
            'fields': ('fullname', 'position', 'role'),
        }),
    )

    # Fieldsets khi thêm user mới
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {
            'fields': ('fullname', 'position', 'role'),
        }),
    )