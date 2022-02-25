"""The base serializers
"""
from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    """Base class for serializers
    """
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
