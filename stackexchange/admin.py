from django.contrib import admin

from stackexchange import models


@admin.register(models.Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin for badges
    """
    list_display = ('name', 'badge_class', 'tag_based')
    list_filter = ('badge_class',)
    search_fields = ('name',)
    ordering = ('name',)


class UserBadgeInline(admin.TabularInline):
    """The user badge inline
    """
    model = models.UserBadge
    readonly_fields = ('date_awarded',)
    extra = 1


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    """Admin for users
    """
    list_display = ('display_name', 'website', 'location', 'created', 'reputation')
    search_fields = ('display_name',)
    inlines = (UserBadgeInline, )
    ordering = ('pk', )


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin for badges
    """
    list_display = ('name', )
    search_fields = ('name',)
    ordering = ('name',)
    autocomplete_fields = ('excerpt', 'wiki')


class PostTagInline(admin.TabularInline):
    """The post tag inline
    """
    model = models.PostTag
    autocomplete_fields = ('tag',)
    extra = 1


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    """Admin for posts
    """
    list_display = ('title', 'type', 'score', 'created', 'last_edit')
    list_filter = ('type',)
    search_fields = ('title',)
    autocomplete_fields = ('owner', 'last_editor')
    ordering = ('pk', )
    inlines = (PostTagInline, )

