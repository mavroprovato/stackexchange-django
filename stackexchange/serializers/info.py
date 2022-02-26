"""The info serializers
"""
from rest_framework import fields

from .base import BaseSerializer


class InfoSerializer(BaseSerializer):
    """The info serializer
    """
    new_active_users = fields.IntegerField(required=False, help_text="Number of new active users")
    total_users = fields.IntegerField(help_text="The total users on the site")
    badges_per_minute = fields.FloatField(required=False, help_text="The number of awarded badges per minute")
    total_badges = fields.IntegerField(help_text="The total number of awarded badges")
    total_votes = fields.IntegerField(help_text="The total votes")
    total_comments = fields.IntegerField(help_text="The total number of comments")
    answers_per_minute = fields.FloatField(required=False, help_text="The answers per minute")
    questions_per_minute = fields.FloatField(required=False, help_text="The questions per minute")
    total_answers = fields.IntegerField(help_text="The total number of answers")
    total_accepted = fields.IntegerField(help_text="The total number of accepted answers")
    total_unanswered = fields.IntegerField(required=False, help_text="The total number of unanswered questions")
    total_questions = fields.IntegerField(help_text="The total number of questions")
    api_revision = fields.CharField(required=False, help_text="The API revision number")
