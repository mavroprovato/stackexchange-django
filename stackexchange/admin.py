from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from stackexchange import models


@admin.register(models.Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin for badges
    """
    list_display = ('name', 'badge_class', 'tag_based')
    list_filter = ('badge_class', 'tag_based')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(models.User)
class UserAdmin(UserAdmin):
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


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    """Admin for posts
    """
    list_display = ('title', 'type', 'score', 'creation_date', 'last_edit_date')
    list_filter = ('type',)
    search_fields = ('title',)
    autocomplete_fields = ('owner', 'last_editor', 'parent', 'accepted_answer')
    ordering = ('-creation_date', )
    inlines = (PostTagInline, )


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for comments
    """
    list_display = ('text', 'user', 'score', 'creation_date')
    list_select_related = ('user', )
    search_fields = ('text',)
    autocomplete_fields = ('post', 'user')
    ordering = ('-creation_date',)
