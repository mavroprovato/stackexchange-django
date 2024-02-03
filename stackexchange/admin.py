"""Admin for the application
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase

from stackexchange import models


@admin.register(models.User)
class UserAdmin(UserAdminBase):
    """Admin for users
    """
    list_display = ('username', 'email', 'display_name', 'staff')
    list_filter = ()
    filter_horizontal = ()
    search_fields = ('username', 'display_name')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'display_name', 'website_url', 'location', 'about')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
