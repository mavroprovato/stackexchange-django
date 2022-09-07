"""The tag views
"""
from django.db.models import QuerySet
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseListViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all tags on the site',
        description=render_to_string('doc/tags/list.md'),
    ),
    info=extend_schema(
        summary='Get tags on the site by their names',
        description=render_to_string('doc/tags/info.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated tag names'
            )
        ]
    ),
    moderator_only=extend_schema(
        summary='Get the tags on the site that only moderators can use',
        description=render_to_string('doc/tags/moderator-only.md'),
    ),
    required=extend_schema(
        summary='Get the tags on the site that fulfill required tag constraints',
        description=render_to_string('doc/tags/required.md'),
    ),
    wikis=extend_schema(
        summary='Get the wiki entries for a set of tags',
        description=render_to_string('doc/tags/wikis.md'),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated tag names'
            )
        ]
    )
)
class TagViewSet(BaseListViewSet):
    """The tag view set
    """
    filter_backends = (filters.OrderingFilter, filters.InNameFilter)

    def get_queryset(self) -> QuerySet | None:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action == 'moderator_only':
            return models.Tag.objects.filter(moderator_only=True)
        if self.action == 'required':
            return models.Tag.objects.filter(required=True)
        if self.action == 'wikis':
            return models.Tag.objects.all().select_related('excerpt', 'wiki').order_by('name')

        return models.Tag.objects.all()

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action == 'wikis':
            return serializers.TagWikiSerializer

        return serializers.TagSerializer

    @property
    def ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'info', 'moderator_only', 'required'):
            return (
                filters.OrderingField('popular', 'award_count', type=int),
                filters.OrderingField('name', direction=enums.OrderingDirection.ASC)
            )

    @property
    def detail_field(self) -> str | None:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        return 'name'

    @property
    def name_field(self) -> str | None:
        """Return the field used for in name filtering.

        :return: The field used for in name filtering.
        """
        if self.action in ('list', 'moderator_only', 'required'):
            return 'name'

    @action(detail=True, url_path='info')
    def info(self, request: Request, *args, **kwargs) -> Response:
        """Get tags on the site by their names.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, url_path='moderator-only')
    def moderator_only(self, request: Request, *args, **kwargs) -> Response:
        """Get the tags on the site that only moderators can use.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, url_path='required')
    def required(self, request: Request, *args, **kwargs) -> Response:
        """Get the tags on the site that fulfill required tag constraints.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='wikis')
    def wikis(self, request: Request, *args, **kwargs) -> Response:
        """Get the wiki entries for a set of tags.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
