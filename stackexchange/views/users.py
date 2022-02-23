"""The users view set.
"""
import typing

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .base import BaseViewSet
from stackexchange import enums, filters, models, serializers


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
    filter_backends = (filters.OrderingFilter, )

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action
        """
        if self.action in ('list', 'retrieve'):
            return models.User.objects.with_badge_counts()
        elif self.action == 'answers':
            return models.Post.objects.filter(type=enums.PostType.ANSWER).select_related('owner', 'parent')
        elif self.action == 'badges':
            return models.UserBadge.objects.select_related('user', 'badge')
        elif self.action == 'comments':
            return models.Comment.objects.select_related('post', 'user')
        elif self.action == 'posts':
            return models.Post.objects.filter(
                type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER)).select_related('owner')
        elif self.action == 'questions':
            return models.Post.objects.filter(type=enums.PostType.QUESTION).select_related('owner').prefetch_related(
                'tags')

    @property
    def detail_field(self) -> typing.Optional[str]:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action in ('answers', 'posts', 'questions'):
            return 'owner'
        elif self.action in ('badges', 'comments'):
            return 'user'

        return super().detail_field

    def get_serializer_class(self):
        """Return the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action in ('list', 'retrieve'):
            return serializers.UserSerializer
        elif self.action == 'answers':
            return serializers.AnswerSerializer
        elif self.action == 'badges':
            return serializers.UserBadgeSerializer
        elif self.action == 'comments':
            return serializers.CommentSerializer
        elif self.action == 'posts':
            return serializers.PostSerializer
        elif self.action == 'questions':
            return serializers.QuestionSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve'):
            return (
                ('reputation', enums.OrderingDirection.DESC.value),
                ('creation', enums.OrderingDirection.DESC.value, 'creation_date'),
                ('name', enums.OrderingDirection.ASC.value, 'display_name')
            )
        elif self.action in ('answers', 'posts', 'questions'):
            return (
                ('activity', enums.OrderingDirection.DESC.value, 'last_activity_date'),
                ('creation', enums.OrderingDirection.DESC.value, 'creation_date'),
                ('votes', enums.OrderingDirection.DESC.value, 'score')
            )
        elif self.action == 'badges':
            return (
                ('name', enums.OrderingDirection.ASC.value, 'badge__name'),
                ('type', enums.OrderingDirection.ASC.value, 'badge__class'),
                ('awarded', enums.OrderingDirection.DESC.value, 'date_awarded')
            )
        elif self.action == 'comments':
            return ('creation', enums.OrderingDirection.DESC.value, 'creation_date'),

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

    @action(detail=True, url_path='questions')
    def questions(self, request: Request, *args, **kwargs) -> Response:
        """Get the questions for a user.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
