"""OpenAPI related classes
"""
from drf_spectacular.openapi import AutoSchema as BaseAutoSchema


class AutoSchema(BaseAutoSchema):
    """The auto schema generation class
    """
    def _is_list_view(self, serializer=None):
        """Return whether a view is a list view. For this project, all views are list views.

        :param serializer: The serializer.
        :return: Always true
        """
        return True
