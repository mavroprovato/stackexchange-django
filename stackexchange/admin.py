"""Admin for the application
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase

from stackexchange import models


@admin.register(models.User)
class UserAdmin(UserAdminBase):
    """Admin for users
    """
    list_display = ('username', 'email', 'staff')
    list_filter = ()
    filter_horizontal = ()
    search_fields = ('username', )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


@admin.register(models.Site)
class SiteAdmin(admin.ModelAdmin):
    """Admin for sites
    """
    list_display = ('name', 'description', 'long_description', 'url')
    search_fields = ('name', )
    ordering = ('name', )
    autocomplete_fields = ('parent', )
