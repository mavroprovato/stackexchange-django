"""The application filters
"""
import dataclasses
import datetime
import typing

from django.db.models import QuerySet
from django.views import View
from django.utils import timezone
from rest_framework.exceptions import ValidationError
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
        else:
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


class DateRangeFilter(BaseFilterBackend):
    """Filter the queryset by date.
    """
    from_date_param = 'fromdate'
    to_date_param = 'todate'

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Filter the queryset based on the from date and to date parameters.

        :param request: The request.
        :param queryset: The queryset.
        :param view: The view.
        :return: Th filtered queryset.
        """
        from stackexchange.views.base import DateFilteringViewSetMixin
        if not isinstance(view, DateFilteringViewSetMixin):
            raise ValueError("The view must implement the DateFilteringViewSetMixin")
        if not view.date_field:
            return queryset

        from_date = self.get_date(request, self.from_date_param)
        if from_date is not None:
            queryset = queryset.filter(**{f'{view.date_field}__gte': from_date})
        to_date = self.get_date(request, self.to_date_param)
        if to_date is not None:
            queryset = queryset.filter(**{f'{view.date_field}__gte': to_date})

        return queryset

    @staticmethod
    def get_date(request: Request, param_name: str) -> typing.Optional[datetime.datetime]:
        """Get a date to filter from the request parameters. The date should be contained in the `param_name` query
        parameter.

        :param request: The request.
        :param param_name: The parameter name.
        :return: The date, if the query parameter contains a value.
        :raises ValueError: If the query parameter value is malformed.
        """
        if request.query_params.get(param_name):
            try:
                return timezone.make_aware(datetime.datetime.strptime(request.query_params.get(param_name), '%Y-%m-%d'))
            except ValueError:
                raise ValidationError({param_name: 'Invalid date'})

    def get_schema_operation_parameters(self, view: View) -> typing.List[dict]:
        """Get the schema operation parameters.

        :param view: The view to get the parameters for.
        :return: The parameters.
        """
        from stackexchange.views.base import DateFilteringViewSetMixin
        if not isinstance(view, DateFilteringViewSetMixin) or not view.date_field:
            return []

        return [
            {
                'name': self.from_date_param,
                'required': False,
                'in': 'query',
                'description': 'Limit results from the start of a date range',
                'schema': {
                    'type': 'string',
                    'format': 'date'
                },
            }, {
                'name': self.to_date_param,
                'required': False,
                'in': 'query',
                'description': 'Limit results from the end of a date range',
                'schema': {
                    'type': 'string',
                    'format': 'date'
                },
            },
        ]
