"""The search view set
"""
from collections.abc import Sequence

from django.db.models import QuerySet
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from stackexchange import enums, exceptions, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all questions on the site',
        description=render_to_string('doc/search/list.md'),
    ),
)
class SearchViewSet(BaseViewSet):
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

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Override the list method in order to raise a validation error if the required parameters are missing.

        :param request: The request.
        :param args: The arguments.
        :param kwargs: The keyword arguments.
        :return: The response.
        """
        if not (
            request.query_params.get(filters.TaggedFilter.param_name) or
            request.query_params.get(filters.InTitleFilter.param_name)
        ):
            raise exceptions.ValidationError(
                f"one of {filters.TaggedFilter.param_name} or {filters.InTitleFilter.param_name} must be set"
            )

        return super().list(request, *args, **kwargs)
