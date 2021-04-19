"""The application views
"""
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all badges on the site', description=' '),
    retrieve=extend_schema(summary='Gets the badge identified by id', description=' '),
    named=extend_schema(summary='Get all non-tagged-based badges', description=' '),
    tags=extend_schema(summary='Get all tagged-based badges', description=' '),
    recipients=extend_schema(summary='Get the recent recipients of the given badges', description=' '),
)
class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """The badge view set
    """
    @action(detail=False, url_path='name')
    def named(self, request: Request) -> Response:
        """Get all the non-tagged-based badges.

        :param request: The request.
        :return: The response.
        """
        return super().list(request)

    @action(detail=False, url_path='tags')
    def tags(self, request: Request) -> Response:
        """Get all the tagged-based badges.

        :param request: The request.
        :return: The response.
        """
        return super().list(request)

    @action(detail=True, url_path='recipients')
    def recipients(self, request: Request, pk=None) -> Response:
        """Get the recent recipients of the given badges.

        :param request: The request.
        :param pk: Not used.
        :return: The response.
        """
        queryset = models.UserBadge.objects.filter(badge=pk).select_related('user', 'badge').order_by('pk')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset.
        """
        queryset = models.Badge.objects.order_by('pk')
        if self.action == 'named':
            queryset = queryset.filter(tag_based=False)
        elif self.action == 'tags':
            queryset = queryset.filter(tag_based=True)

        return queryset

    def get_serializer_class(self):
        """Get the serializer class.

        :return: The serializer class.
        """
        if self.action == 'recipients':
            return serializers.UserBadgeSerializer

        return serializers.BadgeSerializer


@extend_schema_view(
    list=extend_schema(summary='Get all users on the site'),
    retrieve=extend_schema(summary='Gets the badge identified by id'),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """The user view set
    """
    queryset = models.User.objects.prefetch_related('badges__badge').order_by('pk')
    serializer_class = serializers.UserSerializer


@extend_schema_view(
    list=extend_schema(summary='Get all tags on the site'),
    retrieve=extend_schema(summary='Gets the tag identified by id'),
)
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """The tag view set
    """
    queryset = models.Tag.objects.order_by('pk')
    serializer_class = serializers.TagSerializer


@extend_schema_view(
    list=extend_schema(summary='Get all posts on the site'),
    retrieve=extend_schema(summary='Gets the post identified by id'),
)
class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """The post view set
    """
    queryset = models.Post.objects.select_related('owner', 'last_editor').order_by('pk')
    serializer_class = serializers.PostSerializer
