"""The answer serializers
"""
from rest_framework import fields

from stackexchange import models
# from .posts import PostSerializer
#
#
# class AnswerSerializer(PostSerializer):
#     """The answer serializer
#     """
#     is_accepted = fields.SerializerMethodField(help_text="True if the answer is accepted")
#     answer_id = fields.IntegerField(source="pk", help_text="The answer identifier")
#
#     class Meta:
#         model = models.Post
#         fields = (
#             'owner', 'is_accepted', 'score', 'last_activity_date', 'creation_date', 'answer_id', 'question_id',
#             'content_license'
#         )
#
#     @staticmethod
#     def get_is_accepted(post: models.Post) -> bool:
#         """Get weather this answer is accepted.
#
#         :param post: The post.
#         :return: True if the answer is accepted.
#         """
#         return bool(post.accepted_answer_id)
