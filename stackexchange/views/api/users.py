"""The users view set.
"""
import datetime
import typing

from django.db.models import QuerySet, Exists, OuterRef
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all users on the site.',
        description=render_to_string('doc/users/list.md'),
    ),
    retrieve=extend_schema(
        summary='Get the users identified by a set of ids.',
        operation_id='users_retrieve',
        description=render_to_string('doc/users/retrieve.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated user identifiers'
            )
        ]
    ),
    answers=extend_schema(
        summary='Get the answers posted by the users identified by a set of ids.',
        description=render_to_string('doc/users/answers.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated user identifiers'
            )
        ]
    ),
    badges=extend_schema(
        summary=' Get the badges earned by the users identified by a set of ids.',
        description=render_to_string('doc/users/badges.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated user identifiers'
            )
        ]
    ),
    comments=extend_schema(
        summary='Get the comments posted by the users identified by a set of ids.',
        description=render_to_string('doc/users/comments.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated user identifiers'
            )
        ]
    ),
    favorites=extend_schema(
        summary='Get the questions bookmarked (previously known as "favorited") by users identified by a set of ids.',
        description=render_to_string('doc/users/favorites.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated user identifiers'
            )
        ]
    ),
    moderators=extend_schema(
        summary='Get the users who have moderation powers on the site. ',
        description=render_to_string('doc/users/moderators.md'),
    ),
    posts=extend_schema(
        summary='Get all posts (questions and answers) owned by a set of users.',
        description=render_to_string('doc/users/posts.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated user identifiers'
            )
        ]
    ),
    privileges=extend_schema(
        summary='Get the privileges the given user has on the site.',
        description=render_to_string('doc/users/privileges.md'),
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='The user identifier')
        ]
    ),
    questions=extend_schema(
        summary='Get the questions asked by the users identified by a set of ids.',
        description=render_to_string('doc/users/questions.md'),
        parameters=[
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
            return models.Post.objects.filter(type=enums.PostType.ANSWER).select_related('owner', 'question')
        if self.action == 'badges':
            return models.UserBadge.objects.per_user_and_badge()
        if self.action == 'comments':
            return models.Comment.objects.select_related('post', 'user')
        if self.action == 'favorites':
            return models.Post.objects.filter(
                Exists(models.PostVote.objects.filter(user=OuterRef('owner'), type=enums.PostVoteType.FAVORITE))
            ).select_related('owner').prefetch_related('tags')
        if self.action == 'moderators':
            return models.User.objects.with_badge_counts().filter(is_moderator=True)
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
            return serializers.UserBadgeDetailSerializer
        if self.action == 'comments':
            return serializers.CommentSerializer
        if self.action == 'posts':
            return serializers.PostSerializer
        if self.action == 'privileges':
            return serializers.UserPrivilegeSerializer
        if self.action in ('favorites', 'questions'):
            return serializers.QuestionSerializer

        return serializers.UserSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve', 'moderators'):
            return (
                filters.OrderingField('reputation', type=int),
                filters.OrderingField('creation', 'creation_date', type=datetime.date),
                filters.OrderingField('name', 'display_name', enums.OrderingDirection.ASC),
                filters.OrderingField('modified', 'last_modified_date', type=datetime.date),
            )
        if self.action in ('answers', 'favorites', 'posts', 'questions'):
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
            return (
                filters.OrderingField('creation', 'creation_date', type=datetime.date),
                filters.OrderingField('votes', 'score', type=int),
            )

        return None

    @property
    def stable_ordering(self) -> typing.Optional[typing.Sequence[str]]:
        """Get the stable ordering for the view.

        :return: An iterable of strings that define the stable ordering.
        """
        if self.action == 'badges':
            return 'user', 'badge'

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
        if self.action == 'favorites':
            return 'post_votes__user'

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

    @action(detail=True, url_path='favorites')
    def favorites(self, request: Request, *args, **kwargs) -> Response:
        """Get the bookmarked questions for a user.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, url_path='moderators')
    def moderators(self, request: Request, *args, **kwargs) -> Response:
        """Get the users who have moderation powers on the site.

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
