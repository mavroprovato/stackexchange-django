"""The privileges view set
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, serializers
from stackexchange.views import BaseListViewSet


@extend_schema_view(
    list=extend_schema(summary='Returns the earnable privileges on the site', description=' ')
)
class PrivilegesViewSet(BaseListViewSet):
    """The privileges view set
    """
    serializer_class = serializers.PrivilegesSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """The list endpoint. Returns earnable privileges on the site.

        :param request: The request.
        :return: The earnable privileges.
        """
        page = self.paginate_queryset(list(enums.Privilege))
        serializer = self.serializer_class(page, many=True)

        return self.get_paginated_response(serializer.data)
