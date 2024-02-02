"""The question serializers
"""
from rest_framework import fields, serializers

from stackexchange import models
# from .posts import PostSerializer
#
#
# class QuestionSerializer(PostSerializer):
#     """The question serializer
#     """
#     tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name',
#                                         help_text="The tags for the question")
#     is_answered = fields.SerializerMethodField(help_text="True if the question is answered")
#     question_id = fields.IntegerField(source="pk", help_text="The question identifier")
#
#     class Meta:
#         model = models.Post
#         fields = (
#             'tags', 'owner', 'is_answered', 'view_count', 'accepted_answer_id', 'answer_count', 'score',
#             'last_activity_date', 'creation_date', 'last_edit_date', 'question_id', 'content_license', 'title'
#         )
#
#     @staticmethod
#     def get_is_answered(post: models.Post) -> bool:
#         """Get weather this question is answered.
#
#         :param post: The post.
#         :return: True if the question is answered.
#         """
#         return post.answer_count and post.answer_count > 1
