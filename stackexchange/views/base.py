"""The users view set.
"""
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

MAX_RETRIEVE_OBJECTS = 100


class BaseViewSet(viewsets.ReadOnlyModelViewSet):
    """Base view set
    """
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Override the retrieve method in order to accept a list of semicolon separated list of object ids.

        :param request: The request.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :return: The response.
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {f"{self.lookup_field}__in": self.kwargs[lookup_url_kwarg].split(';')[:MAX_RETRIEVE_OBJECTS]}
        queryset = self.filter_queryset(self.get_queryset().filter(**filter_kwargs))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
