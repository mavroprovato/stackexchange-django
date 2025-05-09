"""Admin for the application
"""
from django.contrib import admin

from stackexchange import models


@admin.register(models.Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin for badges.
    """
    list_display = ('name', 'badge_class', 'badge_type')
    list_filter = ('badge_class', 'badge_type')
    search_fields = ('name', )
    ordering = ('name', )


class SiteUserBadgeInline(admin.TabularInline):
    """The user badge inline.
    """
    model = models.UserBadge
    autocomplete_fields = ('badge', )
    extra = 1


@admin.register(models.SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    """Admin for site users.
    """
    list_display = 'display_name', 'creation_date', 'reputation', 'views', 'up_votes', 'down_votes'
    search_fields = 'display_name',
    ordering = 'display_name',
    inlines = (SiteUserBadgeInline, )


class PostTagInline(admin.TabularInline):
    """The post tag inline.
    """
    model = models.PostTag
    autocomplete_fields = ('tag', )
    extra = 1


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    """Admin for posts.
    """
    list_display = ('title', 'type', 'score', 'creation_date', 'last_edit_date')
    list_filter = ('type', )
    search_fields = ('title', )
    autocomplete_fields = ('owner', 'last_editor', 'question', 'accepted_answer')
    inlines = (PostTagInline, )


@admin.register(models.PostVote)
class PostVoteAdmin(admin.ModelAdmin):
    """Admin for post votes.
    """
    list_display = ('post', 'type', 'creation_date', 'user', 'bounty_amount')
    list_filter = ('type', )
    autocomplete_fields = ('post', 'user')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin for tags.
    """
    list_display = ('name', 'award_count', 'moderator_only', 'required')
    list_filter = ('moderator_only', 'required')
    search_fields = ('name', )
    ordering = ('name', )
    autocomplete_fields = ('excerpt', 'wiki')
