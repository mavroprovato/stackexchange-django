"""The application views
"""
from rest_framework import viewsets

from stackexchange import models, serializers


class UserViewSet(viewsets.ModelViewSet):
    """The user view set
    """
    queryset = models.User.objects.prefetch_related('badges__badge').order_by('pk')
    serializer_class = serializers.UserSerializer
