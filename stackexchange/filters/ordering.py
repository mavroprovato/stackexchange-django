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
    ordering: enums.OrderingDirection
    field: str


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
                    'enum': [of.name for of in self.get_ordering_fields(view)]
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
        ordering_fields = self.get_ordering_fields(view)

        if ordering_fields:
            # Get the ordering field from the request, or the first available if it cannot be found
            name = request.query_params.get(self.ordering_name_param)
            ordering_field = next(
                iter(ordering_field for ordering_field in ordering_fields if ordering_field.name == name),
                ordering_fields[0]
            )
            # Customize the sort order if it exists and the request and is valid.
            sort = request.query_params.get(self.ordering_sort_param)
            if sort:
                try:
                    ordering_field.ordering = enums.OrderingDirection(sort.lower())
                except ValueError:
                    pass

            return (
                f"{'-' if ordering_field.ordering == enums.OrderingDirection.DESC else ''}{ordering_field.field}", 'pk'
            )

        return 'pk',

    @staticmethod
    def get_ordering_fields(view: View) -> typing.List[OrderingField]:
        """Get the ordering fields for the view. The method searches for an `ordering_fields` property. The property
        must be an iterable of tuples. The first tuple field is the name of the field to order by, the second is the
        default ordering direction (by default, descending) and the third the name of the database field to order by
        (by default, the same name as the field name).

        :param view: The view to get the ordering fields for.
        :return: The ordering fields.
        """
        fields = []
        ordering_fields = getattr(view, 'ordering_fields')
        if ordering_fields:
            for ordering_field in ordering_fields:
                name = ordering_field[0]
                ordering = enums.OrderingDirection.DESC
                if len(ordering_field) > 1:
                    try:
                        ordering = enums.OrderingDirection(ordering_field[1].lower())
                    except ValueError:
                        pass
                if len(ordering_field) > 2:
                    field = ordering_field[2]
                else:
                    field = name
                fields.append(OrderingField(name, ordering, field))

        return fields

