"""The application serializers
"""
from rest_framework import serializers

from stackexchange import models


class UserSerializer(serializers.ModelSerializer):
    """The user serializer.
    """
    class Meta:
        model = models.User
        fields = ('pk', 'username', 'display_name', 'website', 'about', 'created', 'reputation')
