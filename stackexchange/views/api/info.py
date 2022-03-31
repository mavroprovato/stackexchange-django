"""The info view set
"""
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import serializers, services
from .base import BaseListViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Returns a collection of statistics about the site',
        description=render_to_string('doc/info/list.md'),
    )
)
class InfoViewSet(BaseListViewSet):
    """The info view set
    """
    serializer_class = serializers.InfoSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """The list endpoint. Returns statistics about the site.

        :param request: The request.
        :return: The site statistics.
        """
        queryset = self.paginate_queryset([self.serializer_class(services.get_site_info()).data])

        return self.get_paginated_response(queryset)
