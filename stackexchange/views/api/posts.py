"""The posts view set
"""
import datetime
import typing

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import QuerySet
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all posts (questions and answers) in the system',
        description=render_to_string('doc/posts/list.md'),
    ),
    retrieve=extend_schema(
        summary='Get all posts identified by a set of ids. Useful for when the type of post (question or answer) is '
                'not known',
        description=render_to_string('doc/posts/retrieve.md'),
        operation_id='posts_retrieve',
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated post identifiers'
            )
        ],
    ),
    comments=extend_schema(
        summary='Get comments on the posts (question or answer) identified by a set of ids',
        description=render_to_string('doc/posts/comments.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated post identifiers'
            )
        ],
    ),
    revisions=extend_schema(
        summary='Get revisions on the set of posts in ids',
        description=render_to_string('doc/posts/revisions.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated post identifiers'
            )
        ],
    ),
)
class PostViewSet(BaseViewSet):
    """The post view set
    """
    filter_backends = (filters.OrderingFilter, filters.DateRangeFilter)

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action == 'comments':
            return models.Comment.objects.select_related('post', 'user')
        if self.action == 'revisions':
            return models.PostHistory.objects.values(
                'creation_date', 'post_id', 'post__type', 'content_license', 'user_id', 'comment', 'revision_guid'
            ).annotate(
                types=ArrayAgg('type')
            ).order_by('-creation_date')

        return models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER)).select_related(
            'owner')

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'comments':
            return serializers.CommentSerializer
        if self.action == 'revisions':
            return serializers.PostHistorySerializer

        return serializers.PostSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve'):
            return (
                filters.OrderingField('activity', 'last_activity_date', type=datetime.date),
                filters.OrderingField('creation', 'creation_date', type=datetime.date),
                filters.OrderingField('votes', 'score', type=int)
            )
        if self.action == 'comments':
            return (
                filters.OrderingField('creation', 'creation_date', type=datetime.date),
                filters.OrderingField('votes', 'score', type=int)
            )

        return None

    @property
    def detail_field(self) -> typing.Optional[str]:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action in ('comments', 'revisions'):
            return 'post'

        return super().detail_field

    @property
    def date_field(self) -> str:
        """Return the field used for date filtering.

        :return: The field used for date filtering.
        """
        return 'creation_date'

    @property
    def stable_ordering(self) -> typing.Optional[typing.Sequence[str]]:
        """Get the stable ordering for the view.

        :return: An iterable of strings that define the stable ordering.
        """
        if self.action == 'revisions':
            return '-creation_date',

        return None

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
