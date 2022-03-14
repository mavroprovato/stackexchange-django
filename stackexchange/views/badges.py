"""The badges view set.
"""
import typing

from django.contrib.staticfiles import finders
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all badges on the site', description=open(finders.find('stackexchange/doc/badges/list.md')).read()
    ),
    retrieve=extend_schema(
        summary='Get the badges identified by ids',
        description=open(finders.find('stackexchange/doc/badges/retrieve.md')).read(),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated badge identifiers'
            )
        ]
    ),
    named=extend_schema(
        summary='Get all non-tagged-based badges',
        description=open(finders.find('stackexchange/doc/badges/named.md')).read()
    ),
    recipients=extend_schema(
        summary='Get badges recently awarded on the site',
        description=open(finders.find('stackexchange/doc/badges/recipients.md')).read()
    ),
    recipients_detail=extend_schema(
        summary='Get the recent recipients of the given badges',
        description=open(finders.find('stackexchange/doc/badges/recipients-detail.md')).read(),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated badge identifiers'
            )
        ]
    ),
    tags=extend_schema(
        summary='Get all tagged-based badges',
        description=open(finders.find('stackexchange/doc/badges/tags.md')).read()
    ),
)
class BadgeViewSet(BaseViewSet):
    """The badge view set
    """
    filter_backends = (filters.OrderingFilter, filters.DateRangeFilter, filters.InNameFilter)

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action == 'named':
            return models.Badge.objects.filter(badge_type=enums.BadgeType.NAMED).with_award_count()
        if self.action in ('recipients', 'recipients_detail'):
            return models.UserBadge.objects.select_related('user', 'badge').order_by('-date_awarded')
        if self.action == 'tags':
            return models.Badge.objects.filter(badge_type=enums.BadgeType.TAG_BASED).with_award_count()

        return models.Badge.objects.with_award_count()

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action in ('recipients', 'recipients_detail'):
            return serializers.UserBadgeSerializer

        return serializers.BadgeSerializer

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

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve', 'named', 'tags'):
            return (
                filters.OrderingField('rank', 'badge_class', type=enums.BadgeClass),
                filters.OrderingField('name', direction=enums.OrderingDirection.ASC),
                filters.OrderingField('type', 'badge_type', type=enums.BadgeType)
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
