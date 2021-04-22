"""The application filters
"""
import typing

from rest_framework.filters import BaseFilterBackend


class OrderingFilter(BaseFilterBackend):
    """The ordering filter.
    """
    ORDERING_DESCENDING = 'desc'
    ORDERING_ASCENDING = 'asc'

    ordering_name_param = 'sort'
    ordering_sort_param = 'order'

    def filter_queryset(self, request, queryset, view):
        """Filter the queryset.

        :param request: The request.
        :param queryset: The queryset to filter.
        :param view: The view to filter.
        :return: The filtered queryset.
        """
        return queryset.order_by(*self.get_ordering(request, view))

    def get_ordering(self, request, view) -> typing.List[str]:
        """Return the ordering fields.

        :param request: The request.
        :param view: The view.
        :return: The ordering fields.
        """
        name = request.query_params.get(self.ordering_name_param)
        sort = request.query_params.get(self.ordering_sort_param)
        ordering_fields = getattr(view, 'get_ordering_fields', lambda: {})()

        if not ordering_fields:
            return ['-pk']
        elif name and name in ordering_fields:
            return [f"{'-' if self.ORDERING_DESCENDING == sort else ''}{name}", '-pk']
        elif ordering_fields:
            default_ordering = list(ordering_fields.items())[0]

            return [f"{'-' if self.ORDERING_DESCENDING == default_ordering[1] else ''}{default_ordering[0]}", '-pk']
