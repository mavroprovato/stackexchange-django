"""The date range filter
"""
import datetime
import typing

from django.db.models import QuerySet
from django.views import View
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request


class DateRangeFilter(BaseFilterBackend):
    """Filter the queryset by date.
    """
    from_date_param = 'fromdate'
    to_date_param = 'todate'

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Filter the queryset based on the "from date" and "to date" parameters.

        :param request: The request.
        :param queryset: The queryset.
        :param view: The view.
        :return: The filtered queryset.
        """
        date_field = getattr(view, 'date_field', None)
        if not date_field:
            return queryset

        from_date = self.get_date(request, self.from_date_param)
        if from_date is not None:
            queryset = queryset.filter(**{f'{date_field}__gte': from_date})
        to_date = self.get_date(request, self.to_date_param)
        if to_date is not None:
            queryset = queryset.filter(**{f'{date_field}__lte': to_date})

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
            except ValueError as exception:
                raise ValidationError({param_name: 'Invalid date'}) from exception

    def get_schema_operation_parameters(self, view: View) -> typing.List[dict]:
        """Get the schema operation parameters.

        :param view: The view to get the parameters for.
        :return: The parameters.
        """
        if not getattr(view, 'date_field', None):
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
