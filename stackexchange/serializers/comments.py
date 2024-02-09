"""The comment serializers
"""
from rest_framework import fields

from stackexchange import models
from .posts import PostSerializer
from .users import BaseSiteUserSerializer


class PostCommentSerializer(PostSerializer):
    """The comment serializer
    """
    owner = BaseSiteUserSerializer(source="user", help_text="The user that posted the comment")
    post_id = fields.IntegerField(source="post.pk", help_text="The post identifier")
    comment_id = fields.IntegerField(source="pk", help_text="The comment identifier")

    class Meta:
        model = models.Post
        fields = ('owner', 'score', 'creation_date', 'post_id', 'comment_id', 'content_license')
