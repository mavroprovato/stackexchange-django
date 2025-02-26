"""The comments view set
"""
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema_view, extend_schema

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all comments on the site',
        description=render_to_string('doc/comments/list.md'),
    ),
    retrieve=extend_schema(
        summary='Gets the comment identified by id',
        description=render_to_string('doc/comments/retrieve.md'),
        operation_id='comments_retrieve',
    ),
)
class CommentViewSet(BaseViewSet):
    """The comment view set
    """
    queryset = models.PostComment.objects.select_related('post', 'user')
    serializer_class = serializers.PostCommentSerializer
    filter_backends = (filters.OrderingFilter, filters.DateRangeFilter)
    ordering_fields = (
        filters.OrderingField('creation', 'creation_date', type=enums.OrderingFieldType.DATE),
        filters.OrderingField('votes', 'score', type=enums.OrderingFieldType.INTEGER)
    )
    date_field = 'creation_date'
