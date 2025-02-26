"""The in name filter
"""
from django.db.models import QuerySet
from django.views import View
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request


class InNameFilter(BaseFilterBackend):
    """The in name filter
    """
    param_name = 'inname'

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Filter the queryset based on the in name parameter. If the view defines a `name_field` parameter, then the
        filter only returns results that the `name_field` contains the parameter value, ignoring case. Note, that this
        filter cannot take advantage of any index.

        :param request: The request.
        :param queryset: The queryset.
        :param view: The view.
        :return: The filtered queryset.
        """
        name_field = getattr(view, 'name_field', None)
        if name_field:
            value = request.query_params.get(self.param_name, '').strip()
            if value:
                return queryset.filter(**{f'{name_field}__icontains': value})

        return queryset

    def get_schema_operation_parameters(self, view: View) -> list[dict]:
        """Get the schema operation parameters.

        :param view: The view to get the parameters for.
        :return: The parameters.
        """
        if not getattr(view, 'name_field', None):
            return []

        return [
            {
                'name': self.param_name,
                'required': False,
                'in': 'query',
                'description': 'Filter the results down to just those with a certain substring in their name',
                'schema': {
                    'type': 'string'
                },
            }
        ]
