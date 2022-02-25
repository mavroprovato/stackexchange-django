"""The comment serializers
"""
from rest_framework import fields

from stackexchange import models
from .posts import PostSerializer
from .users import BaseUserSerializer


class CommentSerializer(PostSerializer):
    """The comment serializer
    """
    owner = BaseUserSerializer(source="user")
    comment_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.Post
        fields = ('owner', 'score', 'creation_date', 'post_id', 'comment_id', 'content_license')
