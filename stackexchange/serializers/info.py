"""The info serializers
"""
from rest_framework import fields

from .base import BaseSerializer


class InfoSerializer(BaseSerializer):
    """The info serializer
    """
    new_active_users = fields.IntegerField(required=False)
    total_users = fields.IntegerField()
    badges_per_minute = fields.FloatField(required=False)
    total_badges = fields.IntegerField()
    total_votes = fields.IntegerField()
    total_comments = fields.IntegerField()
    answers_per_minute = fields.FloatField(required=False)
    questions_per_minute = fields.FloatField(required=False)
    total_answers = fields.IntegerField()
    total_accepted = fields.IntegerField()
    total_unanswered = fields.IntegerField(required=False)
    total_questions = fields.IntegerField()
    api_revision = fields.CharField(required=False)
