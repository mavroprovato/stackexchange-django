"""The badge serializer
"""
from rest_framework import fields, serializers

from stackexchange import enums, models
from .base import BaseSerializer


class BadgeSerializer(serializers.ModelSerializer):
    """The badge serializer
    """
    badge_type = fields.SerializerMethodField()
    award_count = fields.IntegerField()
    rank = fields.SerializerMethodField()
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
        return "tag_based" if badge.tag_based else "named"

    @staticmethod
    def get_rank(badge: models.Badge) -> str:
        """Get the badge rank.

        :param badge: The badges.
        :return: The badge type.
        """
        return enums.BadgeClass(badge.badge_class).description


class BadgeCountSerializer(BaseSerializer):
    """The badge count serializer.
    """
    def get_fields(self) -> dict:
        """Return the fields for the serializer. Returns one field for each field class.

        :return: The fields for the serializer.
        """
        serializer_fields = super().get_fields()
        for badge_class in enums.BadgeClass:
            serializer_fields[badge_class.name.lower()] = fields.IntegerField(
                source=f"{badge_class.name.lower()}_count")

        return serializer_fields