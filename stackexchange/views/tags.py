"""The tag views
"""
import typing

from django.contrib.staticfiles import finders
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, filters, models, serializers
from .base import BaseListViewSet


@extend_schema_view(
    list=extend_schema(
        summary='Get all tags on the site',
        description=open(finders.find('stackexchange/doc/tags/list.md')).read()
    ),
    info=extend_schema(
        summary='Get tags on the site by their names',
        description=open(finders.find('stackexchange/doc/tags/info.md')).read(),
        parameters=[
            OpenApiParameter(
                name='id', type=str, location=OpenApiParameter.PATH,
                description='A list of semicolon separated tag names'
            )
        ]
    ),
    wikis=extend_schema(
        summary='Get the wiki entries for a set of tags',
        description=open(finders.find('stackexchange/doc/tags/wikis.md')).read(),
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

    def get_queryset(self) -> typing.Optional[QuerySet]:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
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
        if self.action in ('list', 'info'):
            return (
                filters.OrderingField('popular', 'award_count', type=int),
                filters.OrderingField('name', direction=enums.OrderingDirection.ASC)
            )

        return None

    @property
    def detail_field(self) -> typing.Optional[str]:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action in ('info', 'wikis'):
            return 'name'

        return super().detail_field

    @property
    def name_field(self) -> typing.Optional[str]:
        """Return the field used for in name filtering.

        :return: The field used for in name filtering.
        """
        if self.action == 'list':
            return 'name'

        return None

    @action(detail=True, url_path='info')
    def info(self, request: Request, *args, **kwargs) -> Response:
        """Gets the wikis for tags identified by ids.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='wikis')
    def wikis(self, request: Request, *args, **kwargs) -> Response:
        """Gets the wikis for tags identified by ids.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
