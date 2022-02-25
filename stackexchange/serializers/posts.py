"""The post serializers
"""
from rest_framework import fields, serializers

from stackexchange import enums, models
from .users import BaseUserSerializer


class PostSerializer(serializers.ModelSerializer):
    """The post serializer
    """
    owner = BaseUserSerializer()
    post_type = fields.SerializerMethodField()
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
        return enums.PostType(post.type).description


class PostHistorySerializer(serializers.ModelSerializer):
    """The post history serializer
    """
    user = BaseUserSerializer()
    post_type = fields.SerializerMethodField()

    class Meta:
        model = models.PostHistory
        fields = ('user', 'creation_date', 'post_id', 'post_type', 'content_license', 'comment', 'revision_guid')

    @staticmethod
    def get_post_type(post_history: models.PostHistory) -> str:
        """Get the post type

        :param post_history: The post history.
        :return: The post type.
        """
        return enums.PostHistoryType(post_history.type).description
