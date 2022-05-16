"""The users view set.
"""
import datetime
import typing

from django.db.models import QuerySet, Exists, OuterRef, Count, Sum, F, Subquery
from django.db.models.functions import Coalesce
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
    questions_no_answers=extend_schema(
        summary='Get the questions asked by a set of users, which have no answers.',
        description=render_to_string('doc/users/questions_no_answers.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated user identifiers'
            )
        ]
    ),
    questions_unaccepted=extend_schema(
        summary='Get the questions asked by a set of users, which have at least one answer but no accepted answer.',
        description=render_to_string('doc/users/questions_unaccepted.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=int, location=OpenApiParameter.PATH,
                description='A list of semicolon separated user identifiers'
            )
        ]
    ),
    questions_unanswered=extend_schema(
        summary='Get the questions asked by a set of users, which are not considered to be adequately answered.',
        description=render_to_string('doc/users/questions_unanswered.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=int, location=OpenApiParameter.PATH,
                description='A list of semicolon separated user identifiers'
            )
        ]
    ),
    top_answer_tags=extend_schema(
        summary='Get the top tags (by score) a single user has posted answers in.',
        description=render_to_string('doc/users/top_answer_tags.md'),
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='The user identifier')
        ]
    ),
    top_question_tags=extend_schema(
        summary='Get the top questions a user has posted with a set of tags.',
        description=render_to_string('doc/users/top_question_tags.md'),
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='The user identifier')
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
        if self.action == 'questions_no_answers':
            return models.Post.objects.filter(type=enums.PostType.QUESTION, answer_count=0).select_related(
                'owner').prefetch_related('tags')
        if self.action == 'questions_unaccepted':
            return models.Post.objects.filter(type=enums.PostType.QUESTION).filter(
                answer_count__gt=0, accepted_answer__isnull=True
            ).select_related('owner').prefetch_related('tags')
        if self.action == 'questions_unanswered':
            return models.Post.objects.filter(type=enums.PostType.QUESTION).filter(answer_count__gt=0).filter(
                ~Exists(models.Post.objects.filter(type=enums.PostType.ANSWER, question=OuterRef('pk'), score__gt=0)),
                accepted_answer__isnull=True
            ).select_related('owner').prefetch_related('tags')
        if self.action == 'top_answer_tags':
            return models.Post.objects.filter(
                type=enums.PostType.ANSWER
            ).values(
                user_id=F('owner_id'), tag_name=F('question__tags__name')
            ).annotate(
                answer_count=Count('*'), answer_score=Sum('score'),
                question_count=Coalesce(Subquery(
                    models.Post.objects.filter(
                        type=enums.PostType.QUESTION, owner_id=OuterRef('user_id'), tags__name=OuterRef('tag_name')
                    ).values('owner_id', 'question__tags__name').annotate(
                        question_count=Count('*')
                    ).values('question_count')
                ), 0),
                question_score=Coalesce(Subquery(
                    models.Post.objects.filter(
                        type=enums.PostType.QUESTION, owner_id=OuterRef('user_id'), tags__name=OuterRef('tag_name')
                    ).values('owner_id', 'question__tags__name').annotate(
                        question_score=Sum('score')
                    ).values('question_score')
                ), 0),
            ).order_by('-answer_score')
        if self.action == 'top_question_tags':
            return models.Post.objects.filter(
                type=enums.PostType.QUESTION
            ).values(
                user_id=F('owner_id'), tag_name=F('tags__name')
            ).annotate(
                question_count=Count('*'), question_score=Sum('score'),
                answer_count=Coalesce(Subquery(
                    models.Post.objects.filter(
                        type=enums.PostType.ANSWER, owner_id=OuterRef('user_id'),
                        question__tags__name=OuterRef('tag_name')
                    ).values('owner_id', 'question__tags__name').annotate(
                        answer_count=Count('*')
                    ).values('answer_count')
                ), 0),
                answer_score=Coalesce(Subquery(
                    models.Post.objects.filter(
                        type=enums.PostType.ANSWER, owner_id=OuterRef('user_id'),
                        question__tags__name=OuterRef('tag_name')
                    ).values('owner_id', 'question__tags__name').annotate(
                        answer_score=Sum('score')
                    ).values('answer_score')
                ), 0),
            ).order_by('-question_score')

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
        if self.action in (
            'favorites', 'questions', 'questions_no_answers', 'questions_unaccepted', 'questions_unanswered'
        ):
            return serializers.QuestionSerializer
        if self.action in ('top_answer_tags', 'top_question_tags'):
            return serializers.TopTags

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
        if self.action in (
            'answers', 'favorites', 'posts', 'questions', 'questions_no_answers', 'questions_unaccepted',
            'questions_unanswered'
        ):
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

    @property
    def stable_ordering(self) -> typing.Optional[typing.Sequence[str]]:
        """Get the stable ordering for the view.

        :return: An iterable of strings that define the stable ordering.
        """
        if self.action == 'badges':
            return 'user', 'badge'
        if self.action == 'top_answer_tags':
            return '-answer_score',
        if self.action == 'top_question_tags':
            return '-question_score',

    @property
    def detail_field(self) -> typing.Optional[str]:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action in (
            'answers', 'posts', 'questions', 'questions_no_answers', 'questions_unaccepted', 'questions_unanswered',
            'top_answer_tags', 'top_question_tags'
        ):
            return 'owner'
        if self.action in ('badges', 'comments'):
            return 'user'
        if self.action == 'favorites':
            return 'votes__user'

        return super().detail_field

    @property
    def date_field(self) -> typing.Optional[str]:
        """Return the field used for date filtering.

        :return: The field used for date filtering.
        """
        if self.action == 'badges':
            return 'date_awarded'
        if self.action in ('top_answer_tags', 'top_question_tags'):
            return None

        return 'creation_date'

    @property
    def name_field(self) -> typing.Optional[str]:
        """Return the field used for in name filtering.

        :return: The field used for in name filtering.
        """
        if self.action == 'list':
            return 'display_name'

    @property
    def single_object(self) -> bool:
        """Return true if the action is for a single object.

        :return: True if the action is for a single object.
        """
        if self.action in ('top_answer_tags', 'top_question_tags'):
            return True

        return super().single_object

    @action(detail=True, url_path='answers')
    def answers(self, request: Request, *args, **kwargs) -> Response:
        """Get the answers for a set of users.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='badges')
    def badges(self, request: Request, *args, **kwargs) -> Response:
        """Get the badges for a set of users.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='comments')
    def comments(self, request: Request, *args, **kwargs) -> Response:
        """Get the comments for a set of users.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='favorites')
    def favorites(self, request: Request, *args, **kwargs) -> Response:
        """Get the bookmarked questions for a set of user users.

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
        """Get the posts for a set of users.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='privileges')
    def privileges(self, request: Request, *args, **kwargs) -> Response:
        """Get the privileges for a set of users.

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
        """Get the questions for a set of users.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='questions/no-answers')
    def questions_no_answers(self, request: Request, *args, **kwargs) -> Response:
        """Get the questions asked by a set of users, which have no answers.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='questions/unaccepted')
    def questions_unaccepted(self, request: Request, *args, **kwargs) -> Response:
        """Get the questions asked by a set of users, which have at least one answer but no accepted answer.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='questions/unanswered')
    def questions_unanswered(self, request: Request, *args, **kwargs) -> Response:
        """Get the questions asked by a set of users, which are not considered to be adequately answered.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='top-answer-tags')
    def top_answer_tags(self, request: Request, *args, **kwargs) -> Response:
        """Get the top tags (by score) a single user has posted answers in.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='top-question-tags')
    def top_question_tags(self, request: Request, *args, **kwargs) -> Response:
        """Get the top tags (by score) a single user has asked questions in.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
