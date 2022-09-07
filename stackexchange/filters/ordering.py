"""The ordering filter
"""
import collections.abc
import dataclasses
import datetime
import enum
import functools

from django.db.models import QuerySet
from django.utils import timezone
from django.views import View
from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request

from stackexchange import enums


@dataclasses.dataclass
class OrderingField:
    """Ordering field information
    """
    name: str
    field: str = None
    direction: enums.OrderingDirection = enums.OrderingDirection.DESC
    type: type = str

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
    min_param = 'min'
    max_param = 'max'

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Filter the queryset.

        :param request: The request.
        :param queryset: The queryset to filter.
        :param view: The view to filter.
        :return: The filtered queryset.
        """
        queryset = self.order_queryset(request, queryset, view)
        queryset = self.filter_queryset_by_range(request, queryset, view)

        return queryset

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_ordering_fields(view: View) -> collections.abc.Sequence[OrderingField]:
        """Get the ordering fields from the view.

        :param view: The view.
        :return: The sequence of ordering fields.
        """
        ordering_fields = getattr(view, 'ordering_fields', [])

        if ordering_fields is None:
            return []

        for ordering_field in ordering_fields:
            if not isinstance(ordering_field, OrderingField):
                raise ValueError("The ordering fields must be an instance of the OrderingField class")

        return ordering_fields

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_stable_ordering(view: View) -> collections.abc.Sequence[str]:
        """Get the ordering fields from the view.

        :param view: The view.
        :return: The sequence of ordering fields.
        """
        stable_ordering_fields = getattr(view, 'stable_ordering', None)

        if stable_ordering_fields is None:
            return ['pk']

        return list(stable_ordering_fields)

    def get_ordering_from_request(
            self, request: Request, view: View) -> tuple[OrderingField, enums.OrderingDirection] | None:
        """Get the ordering field and direction from the request.

        :param request: The request.
        :param view: The view ordering fields.
        :return: The ordering field and the direction as a tuple, if it exists in the request.
        """
        ordering_fields = self.get_ordering_fields(view)

        # Get the ordering field parameter from the request
        ordering_name = request.query_params.get(self.ordering_name_param, '').strip()
        ordering_field = None
        if ordering_name:
            for field in ordering_fields:
                if field.name == ordering_name:
                    ordering_field = field
                    break
        # If not provided in the request, use the first ordering field if it exists
        if ordering_field is None and len(ordering_fields) > 0:
            ordering_field = ordering_fields[0]

        # Get the ordering direction from the request
        if ordering_field:
            # Customize the sort order if it exists in the request and is valid.
            ordering_direction = ordering_field.direction
            direction_value = request.query_params.get(self.ordering_sort_param, '').strip()
            if direction_value:
                try:
                    ordering_direction = enums.OrderingDirection(direction_value)
                except ValueError:
                    pass

            return ordering_field, ordering_direction

    def order_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Order the queryset based on the ordering parameters from the request.

        :param request: The request.
        :param queryset: The queryset to order.
        :param view: The view.
        :return: The ordered queryset.
        """
        order_by = list(self.get_stable_ordering(view))
        ordering = self.get_ordering_from_request(request, view)
        if ordering:
            order_by.insert(0, f"{'-' if ordering[1] == enums.OrderingDirection.DESC else ''}{ordering[0].field}")

        return queryset.order_by(*order_by)

    def filter_queryset_by_range(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Filter the queryset based on the min and max parameters from the request.

        :param request: The request.
        :param queryset: The queryset to order.
        :param view: The view.
        :return: The filtered queryset.
        """
        ordering = self.get_ordering_from_request(request, view)
        if ordering:
            min_value = self.get_range_value(request, self.min_param, ordering[0])
            if min_value:
                queryset = queryset.filter(**{f'{ordering[0].field}__gte': min_value})
            max_value = self.get_range_value(request, self.max_param, ordering[0])
            if max_value:
                queryset = queryset.filter(**{f'{ordering[0].field}__lte': max_value})

        return queryset

    @staticmethod
    def get_range_value(request: Request, param_name: str, ordering_field: OrderingField) -> object | None:
        """Get the value of the field to filter for a range.

        :param request: The request.
        :param param_name: The request parameter name.
        :param ordering_field: The ordering field.
        :return: The value, converted to the correct class.
        """
        value_str = request.query_params.get(param_name, '').strip()
        if value_str:
            if ordering_field.type == int:
                try:
                    return int(value_str)
                except ValueError as exception:
                    raise ValidationError({param_name: 'Expected integer'}) from exception
            if ordering_field.type == datetime.date:
                try:
                    return timezone.make_aware(
                        datetime.datetime.strptime(value_str, '%Y-%m-%d'))
                except ValueError as exception:
                    raise ValidationError({param_name: 'Expected date'}) from exception
            if issubclass(ordering_field.type, enum.Enum):
                try:
                    return ordering_field.type[value_str.upper()].value
                except KeyError as exception:
                    raise ValidationError(
                        {param_name: f'Expected one of {",".join(f.name.lower() for f in ordering_field.type)}'}
                    ) from exception

            return value_str

    def get_schema_operation_parameters(self, view: View) -> list[dict]:
        """Get the schema operation parameters.

        :param view: The view to get the parameters for.
        :return: The parameters.
        """
        ordering_fields = self.get_ordering_fields(view)
        if not ordering_fields:
            return []

        return [
            {
                'name': self.ordering_name_param,
                'required': False,
                'in': 'query',
                'description': 'The field to sort by',
                'schema': {
                    'type': 'string',
                    'enum': [of.name for of in ordering_fields]
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
            }, {
                'name': self.min_param,
                'required': False,
                'in': 'query',
                'description': 'The minimum value for the sort field to include for the results',
                'schema': {
                    'type': 'string'
                },
            }, {
                'name': self.max_param,
                'required': False,
                'in': 'query',
                'description': 'The maximum value for the sort field to include for the results',
                'schema': {
                    'type': 'string'
                },
            },
        ]
