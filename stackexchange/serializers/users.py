"""The user serializers
"""
import functools

from rest_framework import fields, serializers

from stackexchange import enums, models
from .base import BaseSerializer


class BaseSiteUserSerializer(serializers.ModelSerializer):
    """The base site user serializer.
    """
    user_id = fields.IntegerField(source="pk", help_text="The user identifier")
    user_type = fields.SerializerMethodField(help_text="The user type")

    class Meta:
        model = models.SiteUser
        fields = ('reputation', 'user_id', 'display_name', 'user_type')

    @staticmethod
    def get_user_type(site_user: models.SiteUser) -> str:
        """Return the site user type.

        :param site_user: The user.
        :return: The user type.
        """
        if not site_user.pk:
            return 'does_not_exist'

        return 'moderator' if site_user.reputation >= enums.Privilege.ACCESS_TO_MODERATOR_TOOLS.reputation \
            else 'registered'


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


class SiteUserSerializer(serializers.ModelSerializer):
    """The user serializer.
    """
    badge_counts = UserBadgeCountSerializer(source="*", help_text="The user badge counts")
    user_id = fields.IntegerField(source="pk", help_text="The user identifier")

    class Meta:
        model = models.SiteUser
        fields = (
            'badge_counts', 'last_access_date', 'last_modified_date',  'reputation', 'creation_date', 'user_id',
            'location', 'website_url', 'display_name'
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
        return BaseSiteUserSerializer(self.get_user_by_id(user_badge['user'])).data

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_user_by_id(user_id: int) -> models.SiteUser:
        """Get a user by id. The result of this method is cached.

        :param user_id: The user id.
        :return: The user.
        """
        return models.SiteUser.objects.get(pk=user_id)

    @staticmethod
    def get_badge_type(user_badge: dict) -> str:
        """Get the user badge type.

        :param user_badge: The user badge info.
        :return: The badge type.
        """
        return str(enums.BadgeType(user_badge['badge__badge_type']).name).lower()

    @staticmethod
    def get_rank(user_badge: dict) -> str:
        """Get the user badge rank.

        :param user_badge: The user badge info.
        :return: The badge type.
        """
        return str(enums.BadgeClass(user_badge['badge__badge_class']).name).lower()


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


class TopTags(BaseSerializer):
    """The top tags serializer
    """
    user_id = fields.IntegerField(help_text="The user identifier")
    answer_count = fields.IntegerField(help_text="The answer count")
    answer_score = fields.IntegerField(help_text="The answer score")
    question_count = fields.IntegerField(help_text="The question count")
    question_score = fields.IntegerField(help_text="The question score")
    tag_name = fields.CharField(help_text="The tag name")
