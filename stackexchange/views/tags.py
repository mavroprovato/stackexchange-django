from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from stackexchange import models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all tags on the site'),
    retrieve=extend_schema(summary='Gets the tag identified by id'),
)
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """The tag view set
    """
    queryset = models.Tag.objects
    serializer_class = serializers.TagSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('count', 'name')
    ordering = ('-count',)
