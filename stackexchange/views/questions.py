from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(summary='Get all questions on the site', description=' '),
    retrieve=extend_schema(summary='Gets the question identified by id', description=' '),
    answers=extend_schema(summary='Gets the answers for a question identified by id', description=' '),
    linked=extend_schema(summary='Get the questions that link to the question identified by an id', description=' '),
    no_answers=extend_schema(summary='Get all questions on the site with no answers', description=' '),
)
class QuestionViewSet(BaseViewSet):
    """The question view set
    """
    filter_backends = (filters.OrderingFilter, )

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action in ('list', 'retrieve'):
            return models.Post.objects.filter(type=enums.PostType.QUESTION).select_related('owner').prefetch_related(
                'tags')
        elif self.action == 'answers':
            return models.Post.objects.filter(type=enums.PostType.ANSWER, parent=self.kwargs['pk']).select_related(
                'owner')
        elif self.action == 'comments':
            return models.Comment.objects.filter(post=self.kwargs['pk']).select_related('user')
        elif self.action == 'linked':
            return models.Post.objects.filter(
                post_links__related_post=self.kwargs['pk'], post_links__type=enums.PostType.QUESTION
            ).select_related('owner').prefetch_related('tags')
        elif self.action == 'no_answers':
            return models.Post.objects.filter(type=enums.PostType.QUESTION, answer_count=0).select_related(
                'owner').prefetch_related('tags')

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action in ('list', 'retrieve', 'linked', 'no_answers'):
            return serializers.QuestionSerializer
        if self.action == 'answers':
            return serializers.AnswerSerializer
        elif self.action == 'comments':
            return serializers.CommentSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve', 'answers', 'linked', 'no_answers'):
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
