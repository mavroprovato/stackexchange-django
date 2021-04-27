"""Answers view set
"""
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets

from stackexchange import filters, models, serializers


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
    filter_backends = (filters.OrderingFilter, )

    def get_ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve'):
            return (
                ('activity', 'desc', 'last_activity_date'), ('creation', 'desc', 'creation_date'),
                ('votes', 'desc', 'score')
            )
