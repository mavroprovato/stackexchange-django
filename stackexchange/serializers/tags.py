"""The tag serializers
"""
from rest_framework import fields, serializers

from stackexchange import models


class TagSerializer(serializers.ModelSerializer):
    """The tag serializer
    """
    class Meta:
        model = models.Tag
        fields = ('count', 'name')


class TagWikiSerializer(serializers.ModelSerializer):
    """The tag wiki serializer
    """
    excerpt_last_edit_date = fields.DateTimeField(source='excerpt.last_edit_date')
    body_last_edit_date = fields.DateTimeField(source='wiki.last_edit_date')
    excerpt = fields.CharField(source='excerpt.body')
    tag_name = fields.CharField(source='name')

    class Meta:
        model = models.Tag
        fields = ('excerpt_last_edit_date', 'body_last_edit_date', 'excerpt', 'tag_name')
