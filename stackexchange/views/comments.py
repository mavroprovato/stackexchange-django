from drf_spectacular.utils import extend_schema_view, extend_schema

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet, DateFilteringViewSetMixin


@extend_schema_view(
    list=extend_schema(summary='Get all comments on the site'),
    retrieve=extend_schema(summary='Gets the comment identified by id'),
)
class CommentViewSet(BaseViewSet, DateFilteringViewSetMixin):
    """The answers view set
    """
    queryset = models.Comment.objects.select_related('post', 'user')
    serializer_class = serializers.CommentSerializer
    filter_backends = (filters.OrderingFilter, filters.DateRangeFilter)

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        return (
            ('creation', enums.OrderingDirection.DESC.value, 'creation_date'),
            ('votes', enums.OrderingDirection.DESC.value, 'score')
        )

    @property
    def date_field(self) -> str:
        """Return the field used for date filtering.

        :return: The field used for date filtering.
        """
        return 'creation_date'
