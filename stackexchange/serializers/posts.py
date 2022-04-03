"""The post serializers
"""
import functools

from rest_framework import fields, serializers

from stackexchange import enums, models
from .users import BaseUserSerializer


class PostSerializer(serializers.ModelSerializer):
    """The post serializer
    """
    owner = BaseUserSerializer(help_text="The post owner")
    post_type = fields.SerializerMethodField(help_text="The post type")
    post_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.Post
        fields = ('owner', 'score', 'last_activity_date', 'creation_date', 'post_type', 'post_id', 'content_license')

    @staticmethod
    def get_post_type(post: models.Post) -> str:
        """Get the post type

        :param post: The post.
        :return: The post type.
        """
        return enums.PostType(post.type).name.lower()


class PostHistorySerializer(serializers.ModelSerializer):
    """The post history serializer
    """
    user = fields.SerializerMethodField(help_text="The user", allow_null=True)
    post_type = fields.SerializerMethodField(help_text="The post type")
    revision_type = fields.SerializerMethodField(help_text="The revision type")

    class Meta:
        model = models.PostHistory
        fields = (
            'user', 'creation_date', 'post_id', 'post_type', 'revision_type', 'content_license', 'comment',
            'revision_guid'
        )

    def get_user(self, post_history: dict) -> dict:
        """Get the user

        :param post_history: The post history.
        :return: The user.
        """
        return BaseUserSerializer(self.get_user_by_id(post_history['user_id'])).data

    @staticmethod
    def get_post_type(post_history: dict) -> str:
        """Get the post type

        :param post_history: The post history.
        :return: The post type.
        """
        return enums.PostType(post_history['post__type']).name.lower()

    @staticmethod
    def get_revision_type(post_history: dict) -> str:
        """Get the revision type

        :param post_history: The post history.
        :return: The post type.
        """
        return 'vote_based' if any(
            enums.PostHistoryType(t).vote_based() for t in post_history['types']
        ) else 'single_user'

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_user_by_id(user_id: int) -> models.User:
        """Get a user by id. The result of this method is cached.

        :param user_id: The user id.
        :return: The user.
        """
        return models.User.objects.get(pk=user_id) if user_id else None
