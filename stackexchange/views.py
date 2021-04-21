"""The application views
"""
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all badges on the site', description=' '),
    retrieve=extend_schema(summary='Gets the badge identified by id', description=' '),
    named=extend_schema(summary='Get all non-tagged-based badges', description=' '),
    tags=extend_schema(summary='Get all tagged-based badges', description=' '),
    recipients=extend_schema(summary='Get the recent recipients of the given badges', description=' '),
)
class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """The badge view set
    """
    filter_backends = (OrderingFilter, )
    ordering_fields = ('name', 'badge_class', 'tag_based')
    ordering = ('name',)

    @action(detail=False, url_path='name')
    def named(self, request: Request) -> Response:
        """Get all the non-tagged-based badges.

        :param request: The request.
        :return: The response.
        """
        return super().list(request)

    @action(detail=False, url_path='tags')
    def tags(self, request: Request) -> Response:
        """Get all the tagged-based badges.

        :param request: The request.
        :return: The response.
        """
        return super().list(request)

    @action(detail=True, url_path='recipients')
    def recipients(self, request: Request, pk=None) -> Response:
        """Get the recent recipients of the given badges.

        :param request: The request.
        :param pk: Not used.
        :return: The response.
        """
        queryset = models.UserBadge.objects.filter(badge=pk).select_related('user', 'badge').order_by('-date_awarded')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        queryset = models.Badge.objects
        if self.action == 'named':
            queryset = queryset.filter(tag_based=False)
        elif self.action == 'tags':
            queryset = queryset.filter(tag_based=True)

        return queryset

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'recipients':
            return serializers.UserBadgeSerializer

        return serializers.BadgeSerializer


@extend_schema_view(
    list=extend_schema(summary='Get all users on the site', description=' '),
    retrieve=extend_schema(summary='Gets the user identified by id', description=' '),
    answers=extend_schema(summary='Get the answers posted by the users identified by id', description=' '),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """The user view set
    """
    filter_backends = (OrderingFilter, )
    ordering_fields = ('reputation', 'creation_date', 'display_name')
    ordering = ('-reputation',)

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action
        """
        if self.action in ('list', 'retrieve'):
            return models.User.objects.prefetch_related('badges__badge')

        return models.User.objects

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

    @action(detail=True, url_path='answers')
    def answers(self, request: Request, pk=None) -> Response:
        """Get the answers for a user.

        :param request: The request.
        :param pk: The user id.
        :return: The response.
        """
        queryset = models.Post.objects.filter(owner=pk, type=models.Post.TYPE_ANSWER).select_related(
            'owner', 'parent').order_by('-last_activity_date')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path='badges')
    def badges(self, request: Request, pk=None) -> Response:
        """Get the answers for a user.

        :param request: The request.
        :param pk: The user id.
        :return: The response.
        """
        queryset = models.UserBadge.objects.filter(user=pk).select_related('user', 'badge').order_by('-date_awarded')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary='Get all tags on the site'),
    retrieve=extend_schema(summary='Gets the tag identified by id'),
)
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """The tag view set
    """
    queryset = models.Tag.objects
    serializer_class = serializers.TagSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('count', 'name')
    ordering = ('-count',)


@extend_schema_view(
    list=extend_schema(summary='Get all posts on the site'),
    retrieve=extend_schema(summary='Gets the post identified by id'),
)
class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """The post view set
    """
    queryset = models.Post.objects.select_related('owner')
    serializer_class = serializers.PostSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('last_activity_date', 'creation_date', 'score')
    ordering = ('-last_activity_date',)


@extend_schema_view(
    list=extend_schema(summary='Get all questions on the site'),
    retrieve=extend_schema(summary='Gets the questions identified by id'),
)
class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """The question view set
    """
    queryset = models.Post.objects.filter(type=models.Post.TYPE_QUESTION).select_related(
        'owner').prefetch_related('tags')
    serializer_class = serializers.QuestionSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('last_activity_date', 'creation_date', 'score')
    ordering = ('-last_activity_date',)


@extend_schema_view(
    list=extend_schema(summary='Get all answers on the site'),
    retrieve=extend_schema(summary='Gets the answers identified by id'),
)
class AnswerViewSet(viewsets.ReadOnlyModelViewSet):
    """The answers view set
    """
    queryset = models.Post.objects.filter(type=models.Post.TYPE_ANSWER).select_related(
        'owner', 'parent').prefetch_related('tags')
    serializer_class = serializers.AnswerSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('last_activity_date', 'creation_date', 'score')
    ordering = ('-last_activity_date',)


@extend_schema_view(
    list=extend_schema(summary='Get all comments on the site'),
    retrieve=extend_schema(summary='Gets the comments identified by id'),
)
class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    """The answers view set
    """
    queryset = models.Comment.objects.select_related('post', 'user')
    serializer_class = serializers.CommentSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ('creation_date', 'score')
    ordering = ('-creation_date',)
