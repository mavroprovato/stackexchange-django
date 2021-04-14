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


class UserSerializer(serializers.ModelSerializer):
    """The user serializer.
    """
    badges = UserBadgeSerializer(many=True)

    class Meta:
        model = models.User
        fields = ('id', 'display_name', 'website', 'about', 'created', 'reputation', 'badges')
