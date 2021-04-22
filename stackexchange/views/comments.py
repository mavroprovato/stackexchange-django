from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from stackexchange import models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all comments on the site'),
    retrieve=extend_schema(summary='Gets the comment identified by id'),
)
class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    """The answers view set
    """
    queryset = models.Comment.objects.select_related('post', 'user')
    serializer_class = serializers.CommentSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('creation_date', 'score')
    ordering = ('-creation_date',)
