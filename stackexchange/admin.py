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
    list_display = (
        'display_name', 'reputation', 'creation_date', 'is_active', 'is_moderator', 'website_url', 'location',
        'creation_date'
    )
    list_filter = ()
    filter_horizontal = ()
    search_fields = ('display_name',)
    ordering = ('pk', )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'display_name', 'website_url', 'location', 'about')}),
        ('Important dates', {'fields': ('creation_date', 'last_modified_date', 'last_access_date')}),
        ('Privileges', {'fields': ('is_active', 'is_moderator', 'is_employee')}),
        ('Statistics', {'fields': ('views', 'up_votes', 'down_votes')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('creation_date', 'last_modified_date', 'last_access_date', 'views', 'up_votes', 'down_votes')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin for tags
    """
    list_display = ('name', 'award_count', 'required', 'moderator_only')
    list_filter = ('required', 'moderator_only')
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


@admin.register(models.PostVote)
class PostVoteAdmin(admin.ModelAdmin):
    """Admin for posts
    """
    list_display = ('post', 'type', 'creation_date', 'user')
    list_select_related = ('post', 'user')
    list_filter = ('type',)
    search_fields = ('post__title',)
    autocomplete_fields = ('post', 'user')
    ordering = ('-creation_date', )


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for comments
    """
    list_display = ('text', 'user', 'score', 'creation_date')
    list_select_related = ('user', )
    search_fields = ('text',)
    autocomplete_fields = ('post', 'user')
    ordering = ('-creation_date',)
