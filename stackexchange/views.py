"""The application views
"""
from rest_framework import viewsets

from stackexchange import models, serializers


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """The badge view set
    """
    queryset = models.Badge.objects.order_by('name')
    serializer_class = serializers.BadgeSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """The user view set
    """
    queryset = models.User.objects.prefetch_related('badges__badge').order_by('pk')
    serializer_class = serializers.UserSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """The tag view set
    """
    queryset = models.Tag.objects.order_by('pk')
    serializer_class = serializers.TagSerializer


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """The post view set
    """
    queryset = models.Post.objects.select_related('owner', 'last_editor').order_by('pk')
    serializer_class = serializers.PostSerializer
