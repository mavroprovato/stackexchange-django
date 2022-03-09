"""The ordering filter
"""
import dataclasses
import datetime
import enum
import typing

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
    type: typing.Type = str

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
        ordering_fields = getattr(view, 'ordering_fields')

        queryset = self.order_queryset(request, queryset, ordering_fields)
        queryset = self.filter_queryset_by_range(request, queryset, ordering_fields)

        return queryset

    def order_queryset(self, request: Request, queryset: QuerySet,
                       ordering_fields: typing.Sequence[OrderingField] = None) -> QuerySet:
        """Order the queryset based on the ordering parameters from the request.

        :param request: The request.
        :param queryset: The queryset to order.
        :param ordering_fields: The view ordering fields.
        :return: The ordered queryset.
        """
        ordering_field = self.get_ordering_field(request, ordering_fields)
        if ordering_field:
            # Customize the sort order if it exists in the request and is valid.
            direction = ordering_field.direction
            direction_value = request.query_params.get(self.ordering_sort_param, '').strip()
            if direction_value:
                try:
                    direction = enums.OrderingDirection(direction_value)
                except ValueError:
                    pass

            return queryset.order_by(
                f"{'-' if direction == enums.OrderingDirection.DESC else ''}{ordering_field.field}", 'pk'
            )

        return queryset.order_by('pk')

    def filter_queryset_by_range(self, request: Request, queryset: QuerySet,
                                 ordering_fields: typing.Sequence[OrderingField] = None) -> QuerySet:
        """Filter the queryset based on the min and max parameters from the request.

        :param request: The request.
        :param queryset: The queryset to order.
        :param ordering_fields: The view ordering fields.
        :return: The filtered queryset.
        """
        ordering_field = self.get_ordering_field(request, ordering_fields)
        if ordering_field:
            min_value = self.get_range_value(request, self.min_param, ordering_field)
            if min_value:
                queryset = queryset.filter(**{f'{ordering_field.field}__gte': min_value})
            max_value = self.get_range_value(request, self.max_param, ordering_field)
            if max_value:
                queryset = queryset.filter(**{f'{ordering_field.field}__lte': max_value})

        return queryset

    @staticmethod
    def get_range_value(request: Request, param_name: str, ordering_field: OrderingField) -> typing.Optional:
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
                except ValueError:
                    raise ValidationError({param_name: 'Expected integer'})
            if ordering_field.type == datetime.date:
                try:
                    return timezone.make_aware(
                        datetime.datetime.strptime(value_str, '%Y-%m-%d'))
                except ValueError as exception:
                    raise ValidationError({param_name: 'Expected date'}) from exception
            if issubclass(ordering_field.type, enum.Enum):
                try:
                    return ordering_field.type[value_str.upper()].value
                except KeyError:
                    raise ValidationError(
                        {param_name: f'Expected one of {",".join(f.name.lower() for f in ordering_field.type)}'})

            return value_str

    def get_ordering_field(self, request: Request, ordering_fields: typing.Sequence[OrderingField]
                           ) -> typing.Optional[OrderingField]:
        """Get the ordering field from the request.

        :param request: The request.
        :param ordering_fields: The view ordering fields.
        :return:
        """
        # Validate that the ordering fields is a sequence of OrderingField instances
        if ordering_fields:
            for ordering_field in ordering_fields:
                if not isinstance(ordering_field, OrderingField):
                    raise ValueError("The ordering fields must be an instance of the OrderingField class")
            # Get the ordering field from the request, or the first available if it cannot be found
            ordering_name = request.query_params.get(self.ordering_name_param, '').strip()
            ordering = None
            if ordering_name:
                for ordering_field in ordering_fields:
                    if ordering_field.name == ordering_name:
                        ordering = ordering_field
            if ordering is None and len(ordering_fields) > 1:
                ordering = ordering_fields[0]

            return ordering

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
