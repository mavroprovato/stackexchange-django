"""The search view set
"""
import datetime

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema

from stackexchange import enums, filters, models, serializers
from .base import BaseListViewSet


@extend_schema_view(
    list=extend_schema(summary='Get all questions on the site', description=' '),
)
class SearchViewSet(BaseListViewSet):
    """The search view set
    """
    filter_backends = (
        filters.OrderingFilter, filters.DateRangeFilter, filters.TaggedFilter, filters.NotTaggedFilter,
        filters.InTitleFilter
    )

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        return models.Post.objects.filter(type=enums.PostType.QUESTION).select_related('owner').prefetch_related(
            'tags')

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        return serializers.QuestionSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action == 'list':
            return (
                filters.OrderingField('activity', 'last_activity_date', type=datetime.date),
                filters.OrderingField('creation', 'creation_date', type=datetime.date),
                filters.OrderingField('votes', 'score', type=int)
            )

        return None
