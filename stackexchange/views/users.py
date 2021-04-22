"""The users view set.
"""
import typing

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import filters, models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all users on the site', description=' '),
    retrieve=extend_schema(summary='Gets the user identified by id', description=' '),
    answers=extend_schema(summary='Get the answers posted by the user identified by id', description=' '),
    badges=extend_schema(summary='Get the badges earned by the user identified by id', description=' '),
    comments=extend_schema(summary='Get the comments posted by the user identified by id', description=' '),
    post=extend_schema(summary='Get all posts (questions and answers) owned by a user', description=' '),
    questions=extend_schema(summary='Get the questions posted by the user identified by id', description=' '),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """The user view set
    """
    filter_backends = (filters.OrderingFilter, )

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action
        """
        if self.action == 'answers':
            return models.Post.objects.filter(owner=self.kwargs['pk'], type=models.Post.TYPE_ANSWER).select_related(
                'owner', 'parent')
        elif self.action == 'badges':
            return models.UserBadge.objects.filter(user=self.kwargs['pk']).select_related('user', 'badge')
        elif self.action == 'comments':
            return models.Comment.objects.filter(user=self.kwargs['pk']).select_related('post', 'user')
        elif self.action == 'posts':
            return models.Post.objects.filter(
                type__in=(models.Post.TYPE_QUESTION, models.Post.TYPE_ANSWER), owner=self.kwargs['pk']
            ).select_related('owner')
        elif self.action == 'questions':
            return models.Post.objects.filter(owner=self.kwargs['pk'], type=models.Post.TYPE_QUESTION).select_related(
                'owner')

        return models.User.objects.prefetch_related('badges__badge')

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

    def get_ordering_fields(self) -> typing.Dict[str, str]:
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve'):
            return {'reputation': 'desc', 'creation_date': 'desc', 'display_name': 'desc'}
        elif self.action in ('answers', 'posts', 'questions'):
            return {'last_activity_date': 'desc', 'creation_date': 'desc', 'votes': 'desc'}
        elif self.action == 'badges':
            return {'badge__name': 'asc', 'badge__badge_class': 'asc'}
        elif self.action == 'comments':
            return {'creation_date': 'desc', 'score': 'desc'}

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

    @action(detail=True, url_path='posts')
    def questions(self, request: Request, *args, **kwargs) -> Response:
        """Get the questions for a user.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
