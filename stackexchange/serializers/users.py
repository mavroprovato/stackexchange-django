"""The user serializers
"""
from rest_framework import fields, serializers

from stackexchange import enums, models
from .badges import BadgeCountSerializer


class BaseUserSerializer(serializers.ModelSerializer):
    """The base user serializer.
    """
    user_id = fields.IntegerField(source="pk", help_text="The user identifier")

    class Meta:
        model = models.User
        fields = ('reputation', 'user_id', 'display_name')


class UserSerializer(serializers.ModelSerializer):
    """The user serializer.
    """
    badge_counts = BadgeCountSerializer(source="*", help_text="The user badge counts")
    user_id = fields.IntegerField(source="pk", help_text="The user identifier")

    class Meta:
        model = models.User
        fields = (
            'badge_counts', 'is_employee', 'reputation', 'creation_date', 'user_id', 'location', 'website_url',
            'display_name'
        )


class UserBadgeSerializer(serializers.ModelSerializer):
    """The user badge serializer
    """
    user = BaseUserSerializer(help_text="The user")
    name = fields.CharField(source='badge.name', help_text="The badge name")
    badge_type = fields.SerializerMethodField(source='badge.badge_type', help_text="The badge type")
    rank = fields.SerializerMethodField(source='badge.rank', help_text="The badge rank")
    badge_id = fields.IntegerField(source='pk', help_text="The badge identifier")

    class Meta:
        model = models.UserBadge
        fields = ('user', 'badge_type', 'rank', 'badge_id', 'name')

    @staticmethod
    def get_badge_type(user_badge: models.UserBadge) -> str:
        """Get the user badge type.

        :param user_badge: The badges.
        :return: The badge type.
        """
        return "tag_based" if user_badge.badge.tag_based else "named"

    @staticmethod
    def get_rank(user_badge: models.UserBadge) -> str:
        """Get the user badge rank.

        :param user_badge: The badges.
        :return: The badge type.
        """
        return enums.BadgeClass(user_badge.badge.badge_class).name.lower()
