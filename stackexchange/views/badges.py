"""The badges view set.
"""
import typing

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet, DateFilteringViewSetMixin


@extend_schema_view(
    list=extend_schema(summary='Get all badges on the site', description=' '),
    retrieve=extend_schema(summary='Get the badges identified by ids', description=' ', parameters=[
        OpenApiParameter(
            name='id', type=str, location=OpenApiParameter.PATH,
            description='A list of semicolon separated badge identifiers'
        )
    ]),
    named=extend_schema(summary='Get all non-tagged-based badges', description=' '),
    recipients=extend_schema(summary='Get badges recently awarded on the site', description=' '),
    recipients_detail=extend_schema(
        summary='Get the recent recipients of the given badges', description=' ', parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated badge identifiers'
            )
        ]
    ),
    tags=extend_schema(summary='Get all tagged-based badges', description=' '),
)
class BadgeViewSet(BaseViewSet, DateFilteringViewSetMixin):
    """The badge view set
    """
    filter_backends = (filters.OrderingFilter, filters.DateRangeFilter, filters.InNameFilter)

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action == 'named':
            return models.Badge.objects.filter(tag_based=False).with_award_count()
        if self.action in ('recipients', 'recipients_detail'):
            return models.UserBadge.objects.select_related('user', 'badge').order_by('-date_awarded')
        if self.action == 'tags':
            return models.Badge.objects.filter(tag_based=True).with_award_count()

        return models.Badge.objects.with_award_count()

    @property
    def detail_field(self) -> typing.Optional[str]:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action == 'recipients_detail':
            return 'badge'

        return super().detail_field

    @property
    def date_field(self) -> typing.Optional[str]:
        """Return the field used for date filtering.

        :return: The field used for date filtering.
        """
        if self.action in ('recipients', 'recipients_detail'):
            return 'date_awarded'

        return None

    @property
    def name_field(self) -> typing.Optional[str]:
        """Return the field used for in name filtering.

        :return: The field used for in name filtering.
        """
        if self.action in ('list', 'named', 'tags'):
            return 'name'

        return None

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action in ('recipients', 'recipients_detail'):
            return serializers.UserBadgeSerializer

        return serializers.BadgeSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve', 'named', 'tags'):
            return (
                ('rank', enums.OrderingDirection.DESC.value, 'badge_class'),
                ('name', enums.OrderingDirection.ASC.value),
                ('type', enums.OrderingDirection.DESC.value, 'tag_based')
            )

        return None

    @action(detail=False, url_path='name')
    def named(self, request: Request, *args, **kwargs) -> Response:
        """Get all the non-tagged-based badges.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, url_path='recipients')
    def recipients(self, request: Request, *args, **kwargs) -> Response:
        """Get badges recently awarded on the site.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='recipients')
    def recipients_detail(self, request: Request, *args, **kwargs) -> Response:
        """Get the recent recipients of the given badges.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, url_path='tags')
    def tags(self, request: Request, *args, **kwargs) -> Response:
        """Get all the tagged-based badges.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
