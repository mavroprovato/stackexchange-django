"""Answers view set
"""
import datetime
import typing

from django.contrib.staticfiles import finders
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all answers on the site',
        description=open(finders.find('stackexchange/doc/answers/list.md')).read()
    ),
    retrieve=extend_schema(
        summary='Get answers identified by a set of ids',
        description=open(finders.find('stackexchange/doc/answers/retrieve.md')).read(),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated answer identifiers'
            )
        ]
    ),
    comments=extend_schema(
        summary='Get comments on the answers identified by a set of ids',
        description=open(finders.find('stackexchange/doc/answers/comments.md')).read(),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated answer identifiers'
            )
        ]
    ),
    questions=extend_schema(
        summary='Gets all questions the answers identified by ids are on',
        description=open(finders.find('stackexchange/doc/answers/questions.md')).read(),
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

    def get_queryset(self) -> typing.Optional[QuerySet]:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action == 'comments':
            return models.Comment.objects.select_related('user')
        if self.action == 'questions':
            return models.Post.objects.select_related('owner').prefetch_related('tags')

        return models.Post.objects.filter(type=enums.PostType.ANSWER).select_related(
            'owner', 'parent').prefetch_related('tags')

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'comments':
            return serializers.CommentSerializer
        if self.action == 'questions':
            return serializers.QuestionSerializer

        return serializers.AnswerSerializer

    @property
    def ordering_fields(self):
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
    def detail_field(self) -> typing.Optional[str]:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action == 'comments':
            return 'post'
        if self.action == 'questions':
            return 'children'

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
