from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import filters, models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all questions on the site', description=' '),
    retrieve=extend_schema(summary='Gets the question identified by id', description=' '),
    answers=extend_schema(summary='Gets the answers for a question identified by id', description=' '),
)
class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """The question view set
    """
    filter_backends = (filters.OrderingFilter, )

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action == 'answers':
            return models.Post.objects.filter(type=models.Post.TYPE_ANSWER, parent=self.kwargs['pk']).select_related(
                'owner')
        elif self.action == 'comments':
            return models.Comment.objects.filter(post=self.kwargs['pk']).select_related('user')
        else:
            return models.Post.objects.filter(type=models.Post.TYPE_QUESTION).select_related('owner').prefetch_related(
                'tags')

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'answers':
            return serializers.AnswerSerializer
        elif self.action == 'comments':
            return serializers.CommentSerializer
        else:
            return serializers.QuestionSerializer

    def get_ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve', 'answers'):
            return (
                ('activity', 'desc', 'last_activity_date'), ('creation', 'desc', 'creation_date'),
                ('votes', 'desc', 'score')
            )
        elif self.action == 'comments':
            return ('creation', 'desc', 'creation_date'), ('votes', 'desc', 'score')

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
