from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all posts on the site', description=' '),
    retrieve=extend_schema(summary='Gets the post identified by id', description=' '),
    comments=extend_schema(summary='Gets the comments for a post identified by id', description=' '),
)
class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """The post view set
    """
    filter_backends = (filters.OrderingFilter, )

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action in ('list', 'retrieve'):
            return models.Post.objects.filter(
                type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER)
            ).select_related('owner')
        elif self.action == 'comments':
            return models.Comment.objects.filter(post=self.kwargs['pk']).select_related('post', 'user')
        elif self.action == 'revisions':
            return models.PostHistory.objects.filter(post=self.kwargs['pk'], user__isnull=False).select_related(
                'post', 'user').order_by('-creation_date')

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action in ('list', 'retrieve'):
            return serializers.PostSerializer
        elif self.action == 'comments':
            return serializers.CommentSerializer
        elif self.action == 'revisions':
            return serializers.PostHistorySerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve'):
            return (
                ('activity', 'desc', 'last_activity_date'), ('creation', 'desc', 'creation_date'),
                ('votes', 'desc', 'score')
            )
        elif self.action == 'comments':
            return ('creation', 'desc', 'creation_date'), ('votes', 'desc', 'score')

    @action(detail=True, url_path='comments')
    def comments(self, request: Request, *args, **kwargs) -> Response:
        """Gets the comments for a post identified by id.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='revisions')
    def revisions(self, request: Request, *args, **kwargs) -> Response:
        """Gets the revision for a post identified by id.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
