from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from stackexchange import models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all questions on the site'),
    retrieve=extend_schema(summary='Gets the question identified by id'),
)
class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """The question view set
    """
    queryset = models.Post.objects.filter(type=models.Post.TYPE_QUESTION).select_related(
        'owner').prefetch_related('tags')
    serializer_class = serializers.QuestionSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('last_activity_date', 'creation_date', 'score')
    ordering = ('-last_activity_date',)
