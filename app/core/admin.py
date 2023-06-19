"""
Django admin customization.
"""
from core.models import User, Recipe
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name', 'last_login', 'is_active']

    fieldsets = (
        (None, {'fields': ('email', 'name', 'password')}),
        (_('Permissions'),
            {'fields':
                (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            } # noqa
        ), # noqa
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    'name',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    ),
            },
        ),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Recipe)
