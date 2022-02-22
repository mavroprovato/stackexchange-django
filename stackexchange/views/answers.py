"""Answers view set
"""
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(summary='Get all answers on the site', description=' '),
    retrieve=extend_schema(summary='Gets the answer identified by id', description=' '),
    comments=extend_schema(summary='Gets the comments for an answer identified by id', description=' '),
    questions=extend_schema(summary='Gets the questions for an answer identified by id', description=' '),
)
class AnswerViewSet(BaseViewSet):
    """The answers view set
    """
    filter_backends = (filters.OrderingFilter, )

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action in ('list', 'retrieve'):
            return models.Post.objects.filter(type=enums.PostType.ANSWER).select_related(
                'owner', 'parent').prefetch_related('tags')
        elif self.action == 'comments':
            return models.Comment.objects.filter(post=self.kwargs['pk']).select_related('user')
        elif self.action == 'questions':
            return models.Post.objects.filter(children=self.kwargs['pk']).select_related('owner').prefetch_related(
                'tags')

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action in ('list', 'retrieve'):
            return serializers.AnswerSerializer
        elif self.action == 'comments':
            return serializers.CommentSerializer
        elif self.action == 'questions':
            return serializers.QuestionSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve', 'questions'):
            return (
                ('activity', enums.OrderingDirection.DESC.value, 'last_activity_date'),
                ('creation', enums.OrderingDirection.DESC.value, 'creation_date'),
                ('votes', enums.OrderingDirection.DESC.value, 'score')
            )
        elif self.action == 'comments':
            return (
                ('creation', enums.OrderingDirection.DESC.value, 'creation_date'),
                ('votes', enums.OrderingDirection.DESC.value, 'score')
            )

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
