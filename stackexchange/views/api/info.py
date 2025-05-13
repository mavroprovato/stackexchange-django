"""The info view set
"""
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema, extend_schema_view

from stackexchange import serializers, services
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Returns a collection of statistics about the site',
        description=render_to_string('doc/info/list.md'),
    )
)
class InfoViewSet(BaseViewSet):
    """The info view set
    """
    serializer_class = serializers.InfoSerializer

    def get_queryset(self) -> list[dict]:
        """Return the site info.

        :return: The site info.
        """
        site_info = services.site_info.SiteInfo(self.request.tenant)

        return [self.serializer_class(site_info.get()).data]
