"""The posts view set
"""
import datetime

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
            return models.PostComment.objects.select_related('post', 'user')

        return models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER)).select_related(
            'owner')

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'comments':
            return serializers.PostCommentSerializer
        if self.action == 'revisions':
            return serializers.PostRevisionSerializer

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

    @property
    def detail_field(self) -> str | None:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action == 'comments':
            return 'post'

        return super().detail_field

    @property
    def date_field(self) -> str:
        """Return the field used for date filtering.

        :return: The field used for date filtering.
        """
        return 'creation_date'

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
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        post_ids = self.kwargs[lookup_url_kwarg].split(';')[:self.MAX_RETRIEVE_OBJECTS]
        result = models.PostHistory.objects.group_by_revision(post_ids=post_ids)
        page = self.paginate_queryset(result)
        if page is not None:
            users = {user.pk: user for user in models.User.objects.filter(pk__in={row['user_id'] for row in page})}
            for row in page:
                row['owner'] = users[row['user_id']] if row['user_id'] else models.User(
                    reputation=None, display_name=row['user_display_name'])
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(page, many=True)

        return Response(serializer.data)
