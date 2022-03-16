"""The privileges serializers
"""
from rest_framework import fields

from stackexchange import enums
from .base import BaseSerializer


class PrivilegeSerializer(BaseSerializer):
    """The privileges serializer
    """
    reputation = fields.IntegerField(help_text="The required reputation to acquire the privilege")
    description = fields.CharField(help_text="The privilege description")
    short_description = fields.SerializerMethodField(help_text="The privilege short description")

    @staticmethod
    def get_short_description(privilege: enums.Privilege) -> str:
        """Get the privilege short description.

        :param privilege: The privilege.
        :return: The privilege short description.
        """
        return privilege.name.lower().replace('_', ' ')
