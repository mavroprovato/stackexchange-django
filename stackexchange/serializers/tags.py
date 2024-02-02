"""The tag serializers
"""
from rest_framework import fields, serializers

from stackexchange import models


# class TagSerializer(serializers.ModelSerializer):
#     """The tag serializer
#     """
#     is_moderator_only = fields.BooleanField(source='moderator_only')
#     is_required = fields.BooleanField(source='required')
#     count = fields.IntegerField(source='award_count', help_text="The tag award count")
#
#     class Meta:
#         model = models.Tag
#         fields = ('is_moderator_only', 'is_required', 'count', 'name')
#
#
# class TagWikiSerializer(serializers.ModelSerializer):
#     """The tag wiki serializer
#     """
#     excerpt_last_edit_date = fields.DateTimeField(
#         source='excerpt.last_edit_date', allow_null=True, help_text="The tag excerpt last edit date")
#     body_last_edit_date = fields.DateTimeField(
#         source='wiki.last_edit_date', allow_null=True, help_text="The tag body last edit date")
#     excerpt = fields.CharField(source='excerpt.body', allow_null=True, help_text="The tag excerpt")
#     tag_name = fields.CharField(source='name', help_text="The tag name")
#
#     class Meta:
#         model = models.Tag
#         fields = ('excerpt_last_edit_date', 'body_last_edit_date', 'excerpt', 'tag_name')
