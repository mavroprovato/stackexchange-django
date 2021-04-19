"""The application views
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from stackexchange import models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all badges on the site'),
    retrieve=extend_schema(summary='Gets the badge identified by id'),
)
class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """The badge view set
    """
    queryset = models.Badge.objects.order_by('name')
    serializer_class = serializers.BadgeSerializer


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
