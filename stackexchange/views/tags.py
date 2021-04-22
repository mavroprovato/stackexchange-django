from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from stackexchange import models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all tags on the site'),
    retrieve=extend_schema(summary='Gets the tag identified by id'),
)
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """The tag view set
    """
    queryset = models.Tag.objects
    serializer_class = serializers.TagSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('count', 'name')
    ordering = ('-count',)


@extend_schema_view(
    list=extend_schema(summary='Get all posts on the site'),
    retrieve=extend_schema(summary='Gets the post identified by id'),
)
class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """The post view set
    """
    queryset = models.Post.objects.filter(
        type__in=(models.Post.TYPE_QUESTION, models.Post.TYPE_ANSWER)).select_related('owner')
    serializer_class = serializers.PostSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('last_activity_date', 'creation_date', 'score')
    ordering = ('-last_activity_date',)
