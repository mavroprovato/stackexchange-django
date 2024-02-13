"""The info view set
"""
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema, extend_schema_view

from stackexchange import filters, models, serializers
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
    queryset = models.Site.objects
    serializer_class = serializers.InfoSerializer
    filter_backends = (filters.SiteFilter, )
