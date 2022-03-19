"""The badge serializer
"""
from rest_framework import fields, serializers

from stackexchange import enums, models
from .users import BaseUserSerializer


class BadgeSerializer(serializers.ModelSerializer):
    """The badge serializer
    """
    badge_type = fields.SerializerMethodField(help_text="The badge type")
    award_count = fields.IntegerField(help_text="The badge award count")
    rank = fields.SerializerMethodField(help_text="The badge rank")
    badge_id = fields.IntegerField(source='pk')

    class Meta:
        model = models.Badge
        fields = ('badge_type', 'award_count', 'rank', 'badge_id', 'name')

    @staticmethod
    def get_badge_type(badge: models.Badge) -> str:
        """Get the badge type.

        :param badge: The badges.
        :return: The badge type.
        """
        return enums.BadgeType(badge.badge_type).name.lower()

    @staticmethod
    def get_rank(badge: models.Badge) -> str:
        """Get the badge rank.

        :param badge: The badges.
        :return: The badge rank.
        """
        return enums.BadgeClass(badge.badge_class).name.lower()


class UserBadgeSerializer(serializers.ModelSerializer):
    """The user badge serializer
    """
    user = BaseUserSerializer(help_text="The user")
    name = fields.CharField(source='badge.name', help_text="The badge name")
    badge_type = fields.SerializerMethodField(source='badge.badge_type', help_text="The badge type")
    rank = fields.SerializerMethodField(source='badge.rank', help_text="The badge rank")
    badge_id = fields.IntegerField(source='badge.pk', help_text="The badge identifier")

    class Meta:
        model = models.UserBadge
        fields = ('user', 'badge_type', 'rank', 'badge_id', 'name')

    @staticmethod
    def get_badge_type(user_badge: models.UserBadge) -> str:
        """Get the user badge type.
        :param user_badge: The badges.
        :return: The badge type.
        """
        return enums.BadgeType(user_badge.badge.badge_type).name.lower()

    @staticmethod
    def get_rank(user_badge: models.UserBadge) -> str:
        """Get the user badge rank.
        :param user_badge: The badges.
        :return: The badge type.
        """
        return enums.BadgeClass(user_badge.badge.badge_class).name.lower()
