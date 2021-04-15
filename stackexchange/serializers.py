"""The application serializers
"""
from django.db.models import QuerySet
from rest_framework import fields, serializers

from stackexchange import models


class BaseSerializer(serializers.Serializer):
    """Base class for serializers
    """
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class BadgeCountSerializer(BaseSerializer):
    """The badge count serializer.
    """
    bronze = fields.SerializerMethodField()
    silver = fields.SerializerMethodField()
    gold = fields.SerializerMethodField()

    @staticmethod
    def get_bronze(user_badges: QuerySet) -> int:
        """Get the number of bronze badges for a user.

        :param user_badges: The user badges.
        :return: The number of bronze badges.
        """
        return BadgeCountSerializer.count_badges(user_badges, models.Badge.CLASS_BRONZE)

    @staticmethod
    def get_silver(user_badges: QuerySet) -> int:
        """Get the number of silver badges for a user.

        :param user_badges: The user badges.
        :return: The number of silver badges.
        """
        return BadgeCountSerializer.count_badges(user_badges, models.Badge.CLASS_SILVER)

    @staticmethod
    def get_gold(user_badges: QuerySet) -> int:
        """Get the number of gold badges for a user.

        :param user_badges: The gold badges.
        :return: The number of gold badges.
        """
        return BadgeCountSerializer.count_badges(user_badges, models.Badge.CLASS_SILVER)

    @staticmethod
    def count_badges(user_badges: QuerySet, badge_class: str) -> int:
        """Count the user badges for a class.

        :param user_badges: The user badges.
        :param badge_class: The badge class.
        :return: The number of badges for the class.
        """
        count = 0
        for user_badge in user_badges.all():
            if user_badge.badge.badge_class == badge_class:
                count += 1

        return count


class BaseUserSerializer(serializers.ModelSerializer):
    """The base user serializer.
    """
    user_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.User
        fields = ('reputation', 'user_id', 'display_name')


class UserSerializer(serializers.ModelSerializer):
    """The user serializer.
    """
    badge_counts = BadgeCountSerializer(source="badges")
    user_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.User
        fields = (
            'badge_counts', 'is_employee', 'reputation', 'creation_date', 'user_id', 'location', 'website_url',
            'display_name'
        )


class PostSerializer(serializers.ModelSerializer):
    """The post serializer
    """
    owner = BaseUserSerializer()
    post_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.Post
        fields = ('owner', 'score', 'last_activity_date', 'creation_date', 'post_id')
