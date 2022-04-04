"""The post serializers
"""
import typing

from rest_framework import fields, serializers

from stackexchange import enums, models
from .base import BaseSerializer
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


class PostRevisionSerializer(BaseSerializer):
    """The post history serializer
    """
    set_community_wiki = fields.SerializerMethodField(
        help_text="True if the history action was to set the post as community wiki")
    is_rollback = fields.SerializerMethodField(help_text="True if the history action was a rollback")
    creation_date = fields.DateTimeField(help_text="The post revision creation date")
    post_id = fields.IntegerField(help_text="The post identifier")
    revision_number = fields.SerializerMethodField(help_text="The post revision number", allow_null=True)
    revision_type = fields.SerializerMethodField(help_text="The revision type")
    revision_guid = fields.CharField(help_text="The revision GUID")

    @staticmethod
    def get_set_community_wiki(post_history: dict) -> bool:
        """Get if the history action was to set the post as community wiki.

        :param post_history: The post history.
        :return: True if the history action was to set the post as community wiki.
        """
        return enums.PostHistoryType.COMMUNITY_OWNED.value in post_history['post_history_types']

    @staticmethod
    def get_is_rollback(post_history: dict) -> bool:
        """Get if the history action was a rollback.

        :param post_history: The post history.
        :return: True if the history action was a rollback.
        """
        return bool(
            {pht.value for pht in enums.PostHistoryType if pht.rollback()} & set(post_history['post_history_types'])
        )

    @staticmethod
    def get_revision_number(post_history: dict) -> typing.Optional[int]:
        """Get the revision number for the post history. Only single user revisions have post histories.

        :param post_history: The post history object.
        :return: The revision number.
        """
        return None if (
            {pht.value for pht in enums.PostHistoryType if pht.vote_based()} & set(post_history['post_history_types'])
        ) else post_history['revision_number']

    @staticmethod
    def get_revision_type(post_history: dict) -> str:
        """Get the revision type. Returns true if any of the post history types for the revision is vote based, false
        otherwise.

        :param post_history: The post history.
        :return: True if the revision is vote based, false otherwise.
        """
        return 'vote_based' if (
            {pht.value for pht in enums.PostHistoryType if pht.vote_based()} & set(post_history['post_history_types'])
        ) else 'single_user'

