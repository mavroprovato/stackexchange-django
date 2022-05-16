"""The user serializers
"""
import functools

from rest_framework import fields, serializers

from stackexchange import enums, models
from .base import BaseSerializer


class BaseUserSerializer(serializers.ModelSerializer):
    """The base user serializer.
    """
    user_id = fields.IntegerField(source="pk", help_text="The user identifier")
    user_type = fields.SerializerMethodField(help_text="The user type")

    class Meta:
        model = models.User
        fields = ('reputation', 'user_id', 'display_name', 'user_type')

    @staticmethod
    def get_user_type(user: models.User) -> str:
        """Return the user type.

        :param user: The user
        :return: The user type
        """
        if not user.pk:
            return 'does_not_exist'

        return 'moderator' if user.is_moderator else 'registered'


class UserBadgeCountSerializer(BaseSerializer):
    """The badge count serializer.
    """
    def get_fields(self) -> dict:
        """Return the fields for the serializer. Returns one field for each field class.

        :return: The fields for the serializer.
        """
        serializer_fields = super().get_fields()
        for badge_class in enums.BadgeClass:
            serializer_fields[badge_class.name.lower()] = fields.IntegerField(
                source=f"{badge_class.name.lower()}_count", help_text=f"The {badge_class.name.lower()} badge count")

        return serializer_fields


class UserSerializer(serializers.ModelSerializer):
    """The user serializer.
    """
    badge_counts = UserBadgeCountSerializer(source="*", help_text="The user badge counts")
    user_id = fields.IntegerField(source="pk", help_text="The user identifier")

    class Meta:
        model = models.User
        fields = (
            'badge_counts', 'is_employee', 'last_modified_date', 'last_access_date', 'reputation', 'creation_date',
            'user_id', 'location', 'website_url', 'display_name'
        )


class UserBadgeDetailSerializer(BaseSerializer):
    """The user badge detail serializer
    """
    user = fields.SerializerMethodField()
    badge_type = fields.SerializerMethodField(help_text="The badge type")
    award_count = fields.IntegerField(help_text="The number of times the user has been awarded the badge")
    rank = fields.SerializerMethodField(help_text="The badge rank")
    badge_id = fields.IntegerField(source='badge', help_text="The badge identifier")
    name = fields.CharField(source='badge__name', help_text="The badge name")

    def get_user(self, user_badge: dict) -> dict:
        """Get the user.

        :param user_badge: The user badge info.
        :return: The user.
        """
        return BaseUserSerializer(self.get_user_by_id(user_badge['user'])).data

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_user_by_id(user_id: int) -> models.User:
        """Get a user by id. The result of this method is cached.

        :param user_id: The user id.
        :return: The user.
        """
        return models.User.objects.get(pk=user_id)

    @staticmethod
    def get_badge_type(user_badge: dict) -> str:
        """Get the user badge type.

        :param user_badge: The user badge info.
        :return: The badge type.
        """
        return enums.BadgeType(user_badge['badge__badge_type']).name.lower()

    @staticmethod
    def get_rank(user_badge: dict) -> str:
        """Get the user badge rank.

        :param user_badge: The user badge info.
        :return: The badge type.
        """
        return enums.BadgeClass(user_badge['badge__badge_class']).name.lower()


class UserPrivilegeSerializer(BaseSerializer):
    """Serializer for a user privilege.
    """
    reputation = fields.IntegerField(help_text="The reputation needed to acquire this privilege")
    description = fields.CharField(help_text="The description for the privilege")
    short_description = fields.SerializerMethodField(help_text="The short description for the privilege")

    @staticmethod
    def get_short_description(privilege: enums.Privilege) -> str:
        """The short description of the privilege. It returns the name of the corresponding enum, replacing underscores
        with spaces and converting the first letter to uppercase.

        :param privilege: The privilege.
        :return: The short description.
        """
        return privilege.name.replace('_', ' ').capitalize()


class TopUserTags(BaseSerializer):
    """The top user tags serializer
    """
    user_id = fields.IntegerField(help_text="The user identifier")
    question_count = fields.IntegerField(help_text="The question count")
    question_score = fields.IntegerField(help_text="The question score")
    tag_name = fields.CharField(help_text="The tag name")
