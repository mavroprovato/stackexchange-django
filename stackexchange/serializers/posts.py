"""The post serializers
"""
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
    user = BaseUserSerializer(help_text="The user")
    post_type = fields.SerializerMethodField(help_text="The post type")

    class Meta:
        model = models.PostHistory
        fields = ('user', 'creation_date', 'post_id', 'post_type', 'content_license', 'comment', 'revision_guid')

    @staticmethod
    def get_post_type(post_history: models.PostHistory) -> str:
        """Get the post type

        :param post_history: The post history.
        :return: The post type.
        """
        return enums.PostType(post_history.post.type).name.lower()
