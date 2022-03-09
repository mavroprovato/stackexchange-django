"""The comments view set
"""
from drf_spectacular.utils import extend_schema_view, extend_schema

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(summary='Get all comments on the site', description=' '),
    retrieve=extend_schema(summary='Gets the comment identified by id', description=' '),
)
class CommentViewSet(BaseViewSet):
    """The answers view set
    """
    queryset = models.Comment.objects.select_related('post', 'user')
    serializer_class = serializers.CommentSerializer
    filter_backends = (filters.OrderingFilter, filters.DateRangeFilter)
    ordering_fields = (
        filters.OrderingField('creation', 'creation_date'),
        filters.OrderingField('votes', 'score')
    )
    date_field = 'creation_date'
