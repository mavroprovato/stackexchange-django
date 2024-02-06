"""Admin for the application
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase

from stackexchange import models


@admin.register(models.Site)
class SiteAdmin(admin.ModelAdmin):
    """Admin for sites.
    """
    list_display = ('name', 'description', 'long_description', 'url')
    search_fields = ('name', )
    ordering = ('name', )
    autocomplete_fields = ('parent', )


@admin.register(models.User)
class UserAdmin(UserAdminBase):
    """Admin for users.
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


class SiteUserBadgeInline(admin.TabularInline):
    """The user badge inline.
    """
    model = models.UserBadge
    autocomplete_fields = ('site', 'badge')
    extra = 1


@admin.register(models.SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    """Admin for site users.
    """
    list_display = ('display_name', 'site', 'creation_date', 'reputation', 'views', 'up_votes', 'down_votes')
    list_filter = ('site', )
    search_fields = ('display_name', )
    ordering = ('site', 'display_name')
    autocomplete_fields = ('site', 'user')
    inlines = (SiteUserBadgeInline, )


@admin.register(models.Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin for badges.
    """
    list_display = ('name', 'site', 'badge_class', 'badge_type')
    list_filter = ('site', 'badge_class', 'badge_type')
    search_fields = ('name', )
    ordering = ('site', 'name')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin for tags.
    """
    list_display = ('name', 'site', 'award_count')
    list_filter = ('site', )
    search_fields = ('name', )
    ordering = ('site', 'name')
