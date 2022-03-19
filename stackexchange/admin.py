"""Admin for the application
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase

from stackexchange import models


@admin.register(models.Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin for badges
    """
    list_display = ('name', 'badge_class', 'badge_type')
    list_filter = ('badge_class', 'badge_type')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(models.User)
class UserAdmin(UserAdminBase):
    """Admin for users
    """
    list_display = ('display_name', 'website_url', 'location', 'reputation', 'creation_date')
    list_filter = ()
    filter_horizontal = ()
    search_fields = ('display_name',)
    ordering = ('pk', )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('display_name', 'website_url', 'location', 'about')}),
        ('Important dates', {'fields': ('last_login', 'creation_date')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('last_login', 'creation_date')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin for tags
    """
    list_display = ('name', 'count')
    search_fields = ('name',)
    ordering = ('name',)
    autocomplete_fields = ('excerpt', 'wiki')


class PostTagInline(admin.TabularInline):
    """The post tag inline
    """
    model = models.PostTag
    autocomplete_fields = ('tag',)
    extra = 1


class PostHistoryInline(admin.TabularInline):
    """The post history inline
    """
    model = models.PostHistory
    readonly_fields = tuple(field.name for field in models.PostHistory._meta.fields)

    def has_add_permission(self, request, obj=None):
        """Overridden in order to disable user from adding new objects.

        :param request: The request.
        :param obj: The objects.
        :return: Always false.
        """
        return False


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    """Admin for posts
    """
    list_display = ('title', 'type', 'score', 'creation_date', 'last_edit_date')
    list_filter = ('type',)
    search_fields = ('title',)
    autocomplete_fields = ('owner', 'last_editor', 'question', 'accepted_answer')
    ordering = ('-creation_date', )
    inlines = (PostTagInline, PostHistoryInline)


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for comments
    """
    list_display = ('text', 'user', 'score', 'creation_date')
    list_select_related = ('user', )
    search_fields = ('text',)
    autocomplete_fields = ('post', 'user')
    ordering = ('-creation_date',)
