"""The post serializers
"""
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


class PostHistorySerializer(BaseSerializer):
    """The post history serializer
    """
    creation_date = fields.DateTimeField(help_text="The post history creation date")
    post_id = fields.IntegerField(help_text="The post identifier")
    revision_number = fields.IntegerField(help_text="The post history revision number")
