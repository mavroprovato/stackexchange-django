import collections
import typing

from rest_framework import pagination
from rest_framework.response import Response


class Pagination(pagination.PageNumberPagination):
    """The default pagination class
    """
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 100

    def get_paginated_response(self, data: typing.Iterable) -> Response:
        """Return the paginated response.

        :param data: The data.
        :return: The paginated response.
        """
        return Response(collections.OrderedDict([
            ('items', data),
            ('has_more', self.page.has_next()),
        ]))
