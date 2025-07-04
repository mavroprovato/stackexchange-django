"""The answer serializers
"""
from rest_framework import fields

from stackexchange import models
from .posts import PostSerializer


class AnswerSerializer(PostSerializer):
    """The answer serializer
    """
    answer_id = fields.IntegerField(source="pk", help_text="The answer identifier")

    class Meta:
        model = models.Post
        fields = (
            'owner', 'is_accepted', 'score', 'last_activity_date', 'creation_date', 'answer_id', 'question_id',
            'content_license'
        )
