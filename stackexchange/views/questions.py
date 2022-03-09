"""The question views
"""
import typing

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(summary='Get all questions on the site', description=' '),
    retrieve=extend_schema(summary='Get the questions identified by a set of ids', description=' ', parameters=[
        OpenApiParameter(
            name='id', type=str, location=OpenApiParameter.PATH,
            description='A list of semicolon separated question identifiers'
        )
    ]),
    answers=extend_schema(
        summary='Get the answers to the questions identified by a set of ids', description=' ',
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated question identifiers'
            )
        ]
    ),
    comments=extend_schema(
        summary='Get the comments on the questions identified by a set of ids', description=' ',
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated question identifiers'
            )
        ]
    ),
    linked=extend_schema(
        summary='Get the questions that link to the questions identified by a set of ids', description=' ', parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated question identifiers'
            )
        ]
    ),
    no_answers=extend_schema(summary='Get all questions on the site with no answers', description=' '),
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
            return models.Comment.objects.select_related('user')
        if self.action == 'linked':
            return models.Post.objects.filter(post_links__type=enums.PostType.QUESTION).select_related(
                'owner').prefetch_related('tags')
        if self.action == 'no_answers':
            return models.Post.objects.filter(type=enums.PostType.QUESTION, answer_count=0).select_related(
                'owner').prefetch_related('tags')

        return models.Post.objects.filter(type=enums.PostType.QUESTION).select_related('owner').prefetch_related(
            'tags')

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'answers':
            return serializers.AnswerSerializer
        if self.action == 'comments':
            return serializers.CommentSerializer

        return serializers.QuestionSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve', 'answers', 'linked', 'no_answers'):
            return (
                filters.OrderingField('activity', 'last_activity_date'),
                filters.OrderingField('creation', 'creation_date'),
                filters.OrderingField('votes', 'score')
            )
        if self.action == 'comments':
            return (
                filters.OrderingField('creation', 'creation_date'),
                filters.OrderingField('votes', 'score')
            )

        return None

    @property
    def detail_field(self) -> typing.Optional[str]:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action == 'answers':
            return 'parent'
        if self.action == 'comments':
            return 'post'
        if self.action == 'linked':
            return 'post_links__related_post'

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

    @action(detail=True, url_path='linked')
    def linked(self, request: Request, *args, **kwargs) -> Response:
        """Get the questions that link to the question identified by an id.

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
