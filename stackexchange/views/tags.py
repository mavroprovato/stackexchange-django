from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets

from stackexchange import filters, models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all tags on the site'),
    retrieve=extend_schema(summary='Gets the tag identified by id'),
)
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """The tag view set
    """
    queryset = models.Tag.objects
    serializer_class = serializers.TagSerializer
    filter_backends = (filters.OrderingFilter, )

    def get_ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve'):
            return ('popular', 'desc', 'count'), ('name', 'asc')
