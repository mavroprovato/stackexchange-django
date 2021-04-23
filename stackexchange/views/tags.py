from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import filters, models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all tags on the site'),
    retrieve=extend_schema(summary='Gets the tag identified by id'),
)
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """The tag view set
    """
    filter_backends = (filters.OrderingFilter, )

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the action.

        :return: The queryset for the action.
        """
        if self.action == 'wikis':
            return models.Tag.objects.filter(pk=self.kwargs['pk']).select_related('excerpt', 'wiki')
        else:
            return models.Tag.objects.all()

    def get_serializer_class(self):
        """Get the serializer class for the action.

        :return: The serializer class for the action.
        """
        if self.action in ('list', 'retrieve'):
            return serializers.TagSerializer
        elif self.action == 'wikis':
            return serializers.TagWikiSerializer

    def get_ordering_fields(self):
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        if self.action in ('list', 'retrieve'):
            return ('popular', 'desc', 'count'), ('name', 'asc')

    @action(detail=True, url_path='wikis')
    def wikis(self, request: Request, *args, **kwargs) -> Response:
        """Get the recent recipients of the given badges.

        :param request: The request.
        :return: The response.
        """
        return super().list(request, *args, **kwargs)
