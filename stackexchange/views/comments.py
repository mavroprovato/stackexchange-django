"""The comments view set
"""
import datetime

from django.contrib.staticfiles import finders
from drf_spectacular.utils import extend_schema_view, extend_schema

from stackexchange import filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all comments on the site',
        description=open(finders.find('stackexchange/doc/comments/list.md')).read()
    ),
    retrieve=extend_schema(
        summary='Gets the comment identified by id',
        description=open(finders.find('stackexchange/doc/comments/retrieve.md')).read()
    ),
)
class CommentViewSet(BaseViewSet):
    """The comment view set
    """
    queryset = models.Comment.objects.select_related('post', 'user')
    serializer_class = serializers.CommentSerializer
    filter_backends = (filters.OrderingFilter, filters.DateRangeFilter)
    ordering_fields = (
        filters.OrderingField('creation', 'creation_date', type=datetime.date),
        filters.OrderingField('votes', 'score', type=int)
    )
    date_field = 'creation_date'
