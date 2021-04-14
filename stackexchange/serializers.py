"""The application serializers
"""
from rest_framework import serializers

from stackexchange import models


class BadgeSerializer(serializers.ModelSerializer):
    """The badge serializer.
    """
    class Meta:
        model = models.Badge
        fields = ('id', 'name', 'badge_class', 'tag_based')


class UserBadgeSerializer(serializers.ModelSerializer):
    """The user badge serializer.
    """
    badge = BadgeSerializer()

    class Meta:
        model = models.UserBadge
        fields = ('badge', 'date_awarded')


class BaseUserSerializer(serializers.ModelSerializer):
    """The base user serializer.
    """
    class Meta:
        model = models.User
        fields = ('id', 'display_name')


class UserSerializer(serializers.ModelSerializer):
    """The user serializer.
    """
    badges = UserBadgeSerializer(many=True)

    class Meta:
        model = models.User
        fields = ('id', 'display_name', 'website', 'about', 'creation_date', 'reputation', 'badges')


class PostSerializer(serializers.ModelSerializer):
    """The post serializer
    """
    owner = BaseUserSerializer()
    last_editor = BaseUserSerializer()

    class Meta:
        model = models.Post
        fields = (
            'id', 'title', 'type', 'created', 'last_edit', 'last_activity', 'score', 'view_count', 'answer_count',
            'comment_count', 'favorite_count', 'owner', 'last_editor'
        )
