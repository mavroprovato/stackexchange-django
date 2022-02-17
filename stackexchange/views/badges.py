"""The badges view set.
"""
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import filters, models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all badges on the site', description=' '),
    retrieve=extend_schema(summary='Gets the badge identified by id', description=' '),
    named=extend_schema(summary='Get all non-tagged-based badges', description=' '),
    recipients=extend_schema(summary='Get badges recently awarded on the site', description=' '),
    recipients_detail=extend_schema(summary='Get the recent recipients of the given badges', description=' '),
    tags=extend_schema(summary='Get all tagged-based badges', description=' '),
)
class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """The badge view set
    """
    filter_backends = (filters.OrderingFilter, )

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action in ('list', 'retrieve'):
            return models.Badge.objects.with_award_count()
        elif self.action == 'named':
            return models.Badge.objects.filter(tag_based=False).with_award_count()
        elif self.action == 'recipients':
            return models.UserBadge.objects.select_related('user', 'badge').order_by('-date_awarded')
        elif self.action == 'recipients_detail':
            return models.UserBadge.objects.filter(badge=self.kwargs['pk']).select_related(
                'user', 'badge').order_by('-date_awarded')
        elif self.action == 'tags':
            return models.Badge.objects.filter(tag_based=True).with_award_count()

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action in ('list', 'retrieve', 'named', 'tags'):
            return serializers.BadgeSerializer
        elif self.action in ('recipients', 'recipients_detail'):
            return serializers.UserBadgeSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve', 'named', 'tags'):
            return ('rank', 'desc', 'badge_class'), ('name', 'asc'), ('type', 'asc', 'tag_based')

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
