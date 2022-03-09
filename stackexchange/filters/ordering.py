"""The ordering filter
"""
import dataclasses
import typing

from django.db.models import QuerySet
from django.views import View
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request

from stackexchange import enums


@dataclasses.dataclass
class OrderingField:
    """Ordering field information
    """
    name: str
    field: str = None
    ordering: enums.OrderingDirection = enums.OrderingDirection.DESC
    type: object = None

    def __post_init__(self):
        """Post init method. Sets the database field to sort by to the field name if the database field name is not set.
        """
        if self.field is None:
            self.field = self.name


class OrderingFilter(BaseFilterBackend):
    """The ordering filter.
    """
    ordering_name_param = 'sort'
    ordering_sort_param = 'order'

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Filter the queryset.

        :param request: The request.
        :param queryset: The queryset to filter.
        :param view: The view to filter.
        :return: The filtered queryset.
        """
        return queryset.order_by(*self.get_ordering(request, view))

    def get_schema_operation_parameters(self, view: View) -> typing.List[dict]:
        """Get the schema operation parameters.

        :param view: The view to get the parameters for.
        :return: The parameters.
        """
        return [
            {
                'name': self.ordering_name_param,
                'required': False,
                'in': 'query',
                'description': 'The field to sort by',
                'schema': {
                    'type': 'string',
                    'enum': [of.name for of in getattr(view, 'ordering_fields', [])]
                },
            }, {
                'name': self.ordering_sort_param,
                'required': False,
                'in': 'query',
                'description': 'The sort direction',
                'schema': {
                    'type': 'string',
                    'enum': [od.value for od in enums.OrderingDirection]
                },
            },
        ]

    def get_ordering(self, request: Request, view: View) -> typing.Iterable[str]:
        """Get the ordering for the view. Returns an iterable of fields that can be used in an order by clause of a
        queryset. If no fields can be found, the primary key is returned.

        :param request: The request.
        :param view: The view.
        :return: The ordering fields.
        """
        ordering_fields = getattr(view, 'ordering_fields', [])
        for ordering_field in ordering_fields:
            if not isinstance(ordering_field, OrderingField):
                raise ValueError("The ordering fields must be an instance of the OrderingField class")

        if ordering_fields:
            # Get the ordering field from the request, or the first available if it cannot be found
            ordering_name = request.query_params.get(self.ordering_name_param, '').strip()
            ordering = None
            if ordering_name:
                for ordering_field in ordering_fields:
                    if ordering_field.name == ordering_name:
                        ordering = ordering_field
            if ordering is None:
                ordering = ordering_fields[0]

            # Customize the sort order if it exists in the request and is valid.
            direction = enums.OrderingDirection.DESC
            direction_value = request.query_params.get(self.ordering_sort_param, '').strip()
            if direction_value:
                try:
                    direction = enums.OrderingDirection(direction_value)
                except ValueError:
                    pass

            return (
                f"{'-' if direction == enums.OrderingDirection.DESC else ''}{ordering.field}", 'pk'
            )

        return 'pk',
