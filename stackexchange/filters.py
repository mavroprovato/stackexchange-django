"""The application filters
"""
import collections.abc
import dataclasses
import enum
import typing

from rest_framework.filters import BaseFilterBackend


class OrderingDirection(enum.Enum):
    """The ordering direction enum
    """
    DESC = 'desc'
    ASC = 'asc'


@dataclasses.dataclass
class OrderingField:
    """Ordering field information
    """
    name: str
    ordering: OrderingDirection
    field: str


class OrderingFilter(BaseFilterBackend):
    """The ordering filter.
    """
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

    def get_ordering(self, request, view) -> typing.Iterable[str]:
        """Get the ordering for the view. Returns an iterable of fields that can be used in an order by clause of a
        queryset. If no fields can be found, the primary key is returned.

        :param request: The request.
        :param view: The view.
        :return: The ordering fields.
        """
        ordering_fields = self.get_ordering_fields(view)

        if ordering_fields:
            # Get the ordering field from the request, or the first available if it cannot be found
            name = request.query_params.get(self.ordering_name_param)
            ordering_field = next(
                iter(ordering_field for ordering_field in ordering_fields if ordering_field.name == name),
                ordering_fields[0])
            # Customize the sort order if it exists and the request and is valid.
            sort = request.query_params.get(self.ordering_sort_param)
            if sort:
                try:
                    ordering_field.ordering = OrderingDirection(sort.lower())
                except ValueError:
                    pass

            return (
                f"{'-' if ordering_field.ordering == OrderingDirection.DESC else ''}{ordering_field.field}", '-pk'
            )
        else:
            return '-pk',

    @staticmethod
    def get_ordering_fields(view) -> typing.List[OrderingField]:
        """Get the ordering fields for the view. This method checks if a `get_ordering_fields` method exists in the
        view. This method should return an iterable. If the element of the iterable is a string, then the ordering
        field is set to this string and the sort is descending by default. If the element is an iterable, then the first
        element is the ordering name, the second is the ordering direction (descending if it does not exist) and the
        third element is the database field name used for the sort (set to the name of the sort, if it does not exist).

        :param view: The view.
        :return: The ordering fields for the view.
        """
        ordering_fields_function = getattr(view, 'get_ordering_fields')
        ordering_fields = []

        if not ordering_fields_function or not ordering_fields_function():
            return ordering_fields

        for ordering_field in ordering_fields_function():
            if isinstance(ordering_field, str):
                ordering_fields.append(OrderingField(ordering_field, OrderingDirection.DESC, ordering_field))
            elif isinstance(ordering_field, collections.abc.Sequence):
                name = ordering_field[0]

                if len(ordering_field) > 1 and isinstance(ordering_field[1], str):
                    try:
                        ordering = OrderingDirection(ordering_field[1].lower())
                    except ValueError:
                        ordering = OrderingDirection.DESC
                else:
                    ordering = OrderingDirection.DESC

                if len(ordering_field) > 2 and isinstance(ordering_field[2], str):
                    field = ordering_field[2]
                else:
                    field = name

                ordering_fields.append(OrderingField(name, ordering, field))

        return ordering_fields
