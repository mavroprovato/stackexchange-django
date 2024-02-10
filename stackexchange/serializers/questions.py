"""The question serializers
"""
from collections.abc import Iterable

from rest_framework import fields, serializers

from stackexchange import models
from .posts import PostSerializer


class QuestionSerializer(PostSerializer):
    """The question serializer
    """
    tags = serializers.SerializerMethodField(help_text="The tags for the question")
    is_answered = fields.SerializerMethodField(help_text="True if the question is answered")
    question_id = fields.IntegerField(source="pk", help_text="The question identifier")

    class Meta:
        model = models.Post
        fields = (
            'tags',
            'owner', 'is_answered', 'view_count', 'accepted_answer_id', 'answer_count', 'score',
            'last_activity_date', 'creation_date', 'last_edit_date', 'question_id', 'content_license', 'title'
        )

    @staticmethod
    def get_tags(post: models.Post) -> Iterable[str]:
        """Get the tag names for this post.

        :param post: The post.
        :return: The tag names.
        """
        return (pt.tag.name for pt in post.tags.all())

    @staticmethod
    def get_is_answered(post: models.Post) -> bool:
        """Get whether this question is answered.

        :param post: The post.
        :return: True if the question is answered.
        """
        return post.answer_count and post.answer_count > 1
