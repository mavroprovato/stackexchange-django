"""The search view set
"""
from collections.abc import Sequence

from django.db.models import QuerySet
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.serializers import Serializer

from stackexchange import enums, filters, models, serializers
from .base import BaseListViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all questions on the site',
        description=render_to_string('doc/search/list.md'),
    ),
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

    def get_serializer_class(self) -> type[Serializer]:
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        return serializers.QuestionSerializer

    @property
    def ordering_fields(self) -> Sequence[filters.OrderingField] | None:
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        return (
            filters.OrderingField('activity', 'last_activity_date', type=enums.OrderingFieldType.DATE),
            filters.OrderingField('creation', 'creation_date', type=enums.OrderingFieldType.DATE),
            filters.OrderingField('votes', 'score', type=enums.OrderingFieldType.INTEGER)
        )
