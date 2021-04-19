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
)
class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """The badge view set
    """
    queryset = models.Badge.objects
    serializer_class = serializers.BadgeSerializer

    @action(detail=False, url_path='name')
    def named(self, request: Request, *args, **kwargs) -> Response:
        """Get all the non-tagged-based badges

        :param request: The request.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, url_path='tags')
    def tags(self, request: Request, *args, **kwargs) -> Response:
        """Get all the tagged-based badges

        :param request: The request.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset.
        """
        queryset = self.queryset.order_by('name')
        if self.action == 'named':
            queryset = queryset.filter(tag_based=False)
        elif self.action == 'tags':
            queryset = queryset.filter(tag_based=True)

        return queryset


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
