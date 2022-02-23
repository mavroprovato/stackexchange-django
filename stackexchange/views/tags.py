from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema

from stackexchange import enums, filters, models, serializers
from .base import BaseListViewSet


@extend_schema_view(
    list=extend_schema(summary='Get all tags on the site'),
)
class TagViewSet(BaseListViewSet):
    """The tag view set
    """
    filter_backends = (filters.OrderingFilter, )

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action == 'list':
            return models.Tag.objects.all()

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'list':
            return serializers.TagSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action == 'list':
            return ('popular', enums.OrderingDirection.DESC.value, 'count'), ('name', enums.OrderingDirection.ASC.value)
