"""The users view set.
"""
import datetime
import typing

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(summary='Get all users on the site', description=' ',),
    retrieve=extend_schema(summary='Gets the user identified by id', description=' ', parameters=[
        OpenApiParameter(
            name='id', type=str, location=OpenApiParameter.PATH,
            description='A list of semicolon separated user identifiers'
        )
    ]),
    answers=extend_schema(summary='Get the answers posted by the user identified by id', description=' ', parameters=[
        OpenApiParameter(
            name='id', type=str, location=OpenApiParameter.PATH,
            description='A list of semicolon separated user identifiers'
        )
    ]),
    badges=extend_schema(summary='Get the badges earned by the user identified by id', description=' ', parameters=[
        OpenApiParameter(
            name='id', type=str, location=OpenApiParameter.PATH,
            description='A list of semicolon separated user identifiers'
        )
    ]),
    comments=extend_schema(summary='Get the comments posted by the user identified by id', description=' ', parameters=[
        OpenApiParameter(
            name='id', type=str, location=OpenApiParameter.PATH,
            description='A list of semicolon separated user identifiers'
        )
    ]),
    posts=extend_schema(summary='Get all posts (questions and answers) owned by a user', description=' ', parameters=[
        OpenApiParameter(
            name='id', type=str, location=OpenApiParameter.PATH,
            description='A list of semicolon separated user identifiers'
        )
    ]),
    privileges=extend_schema(summary='Returns the privileges a user has', description=' ', parameters=[
        OpenApiParameter(
            name='id', type=int, location=OpenApiParameter.PATH, description='The user identifier'
        )
    ]),
    questions=extend_schema(
        summary='Get the questions posted by the user identified by id', description=' ', parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated user identifiers'
            )
        ]
    ),
)
class UserViewSet(BaseViewSet):
    """The user view set
    """
    filter_backends = (filters.OrderingFilter, filters.DateRangeFilter, filters.InNameFilter)

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action
        """
        if self.action == 'answers':
            return models.Post.objects.filter(type=enums.PostType.ANSWER).select_related('owner', 'parent')
        if self.action == 'badges':
            return models.UserBadge.objects.select_related('user', 'badge')
        if self.action == 'comments':
            return models.Comment.objects.select_related('post', 'user')
        if self.action == 'posts':
            return models.Post.objects.filter(
                type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER)).select_related('owner')
        if self.action == 'questions':
            return models.Post.objects.filter(type=enums.PostType.QUESTION).select_related('owner').prefetch_related(
                'tags')

        return models.User.objects.with_badge_counts()

    def get_serializer_class(self):
        """Return the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'answers':
            return serializers.AnswerSerializer
        if self.action == 'badges':
            return serializers.UserBadgeSerializer
        if self.action == 'comments':
            return serializers.CommentSerializer
        if self.action == 'posts':
            return serializers.PostSerializer
        if self.action == 'privileges':
            return serializers.UserPrivilegesSerializer
        if self.action == 'questions':
            return serializers.QuestionSerializer

        return serializers.UserSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve'):
            return (
                filters.OrderingField('reputation', type=int),
                filters.OrderingField('creation', 'creation_date', type=datetime.date),
                filters.OrderingField('name', 'display_name', enums.OrderingDirection.ASC),
            )
        if self.action in ('answers', 'posts', 'questions'):
            return (
                filters.OrderingField('activity', 'last_activity_date', type=datetime.date),
                filters.OrderingField('creation', 'creation_date', type=datetime.date),
                filters.OrderingField('votes', 'score', type=int),
            )
        if self.action == 'badges':
            return (
                filters.OrderingField('rank', 'badge__badge_class', type=enums.BadgeClass),
                filters.OrderingField('name', 'badge__name', enums.OrderingDirection.ASC),
                filters.OrderingField('type', 'badge__badge_type', type=enums.BadgeType),
                filters.OrderingField('awarded', 'date_awarded', type=datetime.date),
            )
        if self.action == 'comments':
            return filters.OrderingField('creation', 'creation_date', type=datetime.date),

        return None

    @property
    def detail_field(self) -> typing.Optional[str]:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action in ('answers', 'posts', 'questions'):
            return 'owner'
        if self.action in ('badges', 'comments'):
            return 'user'

        return super().detail_field

    @property
    def date_field(self) -> str:
        """Return the field used for date filtering.

        :return: The field used for date filtering.
        """
        if self.action == 'badges':
            return 'date_awarded'

        return 'creation_date'

    @property
    def name_field(self) -> typing.Optional[str]:
        """Return the field used for in name filtering.

        :return: The field used for in name filtering.
        """
        if self.action == 'list':
            return 'display_name'

        return None

    @action(detail=True, url_path='answers')
    def answers(self, request: Request, *args, **kwargs) -> Response:
        """Get the answers for a user.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='badges')
    def badges(self, request: Request, *args, **kwargs) -> Response:
        """Get the badges for a user.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='comments')
    def comments(self, request: Request, *args, **kwargs) -> Response:
        """Get the comments for a user.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='posts')
    def posts(self, request: Request, *args, **kwargs) -> Response:
        """Get the posts for a user.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='privileges')
    def privileges(self, request: Request, *args, **kwargs) -> Response:
        """Get the privileges for a user.

        :param request: The request.
        :return: The response.
        """
        user = get_object_or_404(models.User, pk=kwargs['pk'])
        privileges = self.paginate_queryset(
            [privilege for privilege in enums.Privilege if user.reputation >= privilege.reputation]
        )
        serializer = self.get_serializer(privileges, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path='questions')
    def questions(self, request: Request, *args, **kwargs) -> Response:
        """Get the questions for a user.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
