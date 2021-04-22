from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from stackexchange import models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all answers on the site'),
    retrieve=extend_schema(summary='Gets the answer identified by id'),
)
class AnswerViewSet(viewsets.ReadOnlyModelViewSet):
    """The answers view set
    """
    queryset = models.Post.objects.filter(type=models.Post.TYPE_ANSWER).select_related(
        'owner', 'parent').prefetch_related('tags')
    serializer_class = serializers.AnswerSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('last_activity_date', 'creation_date', 'score')
    ordering = ('-last_activity_date',)
