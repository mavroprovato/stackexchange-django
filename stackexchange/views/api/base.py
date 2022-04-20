"""The users view set.
"""
import typing

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class BaseListViewSet(GenericViewSet):
    """Base list view set
    """
    # The maximum number of object to retrieve for detail actions
    MAX_RETRIEVE_OBJECTS = 100

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Override the retrieve method in order to accept a list of semicolon separated list of object ids.

        :param request: The request.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :return: The response.
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg in self.kwargs:
            if self.detail_field is None:
                raise AssertionError(f'Detail field for action {self.action} should not be None')
            queryset = queryset.filter(**{
                f"{self.detail_field}__in": self.kwargs[lookup_url_kwarg].split(';')[:self.MAX_RETRIEVE_OBJECTS]
            })

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @property
    def detail_field(self) -> typing.Optional[str]:
        """Return the field used to filter detail actions.

        :return: The fields used to filter detail actions.
        """
        if self.action == 'retrieve':
            return 'pk'


class BaseViewSet(BaseListViewSet):
    """Base view set
    """
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """The retrieve action.

        :param request: The request.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :return: The response.
        """
        return self.list(request, *args, **kwargs)
