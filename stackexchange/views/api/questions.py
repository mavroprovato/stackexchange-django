"""The question views
"""
import datetime

from django.db.models import QuerySet, Exists, OuterRef
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all questions on the site.',
        description=render_to_string('doc/questions/list.md'),
    ),
    retrieve=extend_schema(
        summary='Get the questions identified by a set of ids.',
        description=render_to_string('doc/questions/retrieve.md'),
        operation_id='questions_retrieve',
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated question identifiers'
            )
        ]
    ),
    answers=extend_schema(
        summary=' Get the answers to the questions identified by a set of ids.',
        description=render_to_string('doc/questions/answers.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated question identifiers'
            )
        ]
    ),
    comments=extend_schema(
        summary='Get the comments on the questions identified by a set of ids.',
        description=render_to_string('doc/questions/comments.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated question identifiers'
            )
        ]
    ),
    no_answers=extend_schema(
        summary='Get all questions on the site with no answers.',
        description=render_to_string('doc/questions/no_answers.md'),
    ),
    unanswered=extend_schema(
        summary='Get all questions the site considers unanswered.',
        description=render_to_string('doc/questions/unanswered.md'),
    ),
)
class QuestionViewSet(BaseViewSet):
    """The question view set
    """
    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action == 'answers':
            return models.Post.objects.filter(type=enums.PostType.ANSWER).select_related('owner')
        if self.action == 'comments':
            return models.PostComment.objects.select_related('user')
        if self.action == 'no_answers':
            return models.Post.objects.filter(type=enums.PostType.QUESTION, answer_count=0).select_related(
                'owner').prefetch_related('tags')
        if self.action == 'unanswered':
            return models.Post.objects.filter(type=enums.PostType.QUESTION).filter(~Exists(
                models.Post.objects.filter(question=OuterRef('pk'), type=enums.PostType.ANSWER, score__gt=0)
            )).select_related('owner').prefetch_related('tags')

        return models.Post.objects.filter(type=enums.PostType.QUESTION).select_related('owner').prefetch_related(
            'tags')

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'answers':
            return serializers.AnswerSerializer
        if self.action == 'comments':
            return serializers.PostCommentSerializer

        return serializers.QuestionSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve', 'answers', 'linked', 'no_answers', 'unanswered'):
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
        if self.action == 'answers':
            return 'question'
        if self.action == 'comments':
            return 'post'

        return super().detail_field

    @property
    def date_field(self) -> str:
        """Return the field used for date filtering.

        :return: The field used for date filtering.
        """
        return 'creation_date'

    @property
    def filter_backends(self):
        """Return the filter backends for the action.

        :return: The filter backends for the action.
        """
        if self.action in ('list', 'no_answers'):
            return filters.OrderingFilter, filters.DateRangeFilter, filters.TaggedFilter

        return filters.OrderingFilter, filters.DateRangeFilter

    @action(detail=True, url_path='answers')
    def answers(self, request: Request, *args, **kwargs) -> Response:
        """Gets the answers for a question identified by id.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='comments')
    def comments(self, request: Request, *args, **kwargs) -> Response:
        """Gets the comments for question identified by id.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, url_path='no-answers')
    def no_answers(self, request: Request, *args, **kwargs) -> Response:
        """Get all questions on the site with no answers.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, url_path='unanswered')
    def unanswered(self, request: Request, *args, **kwargs) -> Response:
        """Get all questions the site considers unanswered.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
