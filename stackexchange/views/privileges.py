"""The privileges view set
"""
from django.contrib.staticfiles import finders
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, serializers
from stackexchange.views import BaseListViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all the privileges available on the site',
        description=open(finders.find('stackexchange/doc/privileges/list.md')).read()
    )
)
class PrivilegesViewSet(BaseListViewSet):
    """The privileges view set
    """
    serializer_class = serializers.PrivilegeSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """The list endpoint. Returns earnable privileges on the site.

        :param request: The request.
        :return: The earnable privileges.
        """
        page = self.paginate_queryset(list(enums.Privilege))
        serializer = self.serializer_class(page, many=True)

        return self.get_paginated_response(serializer.data)
