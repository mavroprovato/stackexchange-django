"""Answers view set
"""
from collections.abc import Sequence
import datetime

from django.db.models import QuerySet
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all answers on the site',
        description=render_to_string('doc/answers/list.md')
    ),
    retrieve=extend_schema(
        summary='Get answers identified by a set of ids',
        operation_id='answers_retrieve',
        description=render_to_string('doc/answers/retrieve.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated answer identifiers'
            )
        ]
    ),
    comments=extend_schema(
        summary='Get comments on the answers identified by a set of ids',
        description=render_to_string('doc/answers/comments.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated answer identifiers'
            )
        ]
    ),
    questions=extend_schema(
        summary='Gets all questions the answers identified by ids are on',
        description=render_to_string('doc/answers/questions.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated answer identifiers'
            )
        ]
    ),
)
class AnswerViewSet(BaseViewSet):
    """The answers view set
    """
    filter_backends = (filters.OrderingFilter, filters.DateRangeFilter)

    def get_queryset(self) -> QuerySet | None:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action == 'comments':
            return models.PostComment.objects.select_related('user', 'post')
        if self.action == 'questions':
            return models.Post.objects.filter(type=enums.PostType.QUESTION).select_related('owner').prefetch_related(
                'tags')

        return models.Post.objects.filter(type=enums.PostType.ANSWER).select_related(
            'owner', 'question').prefetch_related('tags')

    def get_serializer_class(self) -> type[Serializer]:
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'comments':
            return serializers.PostCommentSerializer
        if self.action == 'questions':
            return serializers.QuestionSerializer

        return serializers.AnswerSerializer

    @property
    def ordering_fields(self) -> Sequence[filters.OrderingField] | None:
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve', 'questions'):
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
    def detail_field(self) -> str | None:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action == 'comments':
            return 'post'
        if self.action == 'questions':
            return 'answers'

        return super().detail_field

    @property
    def date_field(self) -> str:
        """Return the field used for date filtering.

        :return: The field used for date filtering.
        """
        return 'creation_date'

    @action(detail=True, url_path='comments')
    def comments(self, request: Request, *args, **kwargs) -> Response:
        """Gets the comments for an answer identified by id.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='questions')
    def questions(self, request: Request, *args, **kwargs) -> Response:
        """Gets the questions for an answer identified by id.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
