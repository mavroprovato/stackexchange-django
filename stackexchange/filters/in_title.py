"""The questions in title filter
"""
import typing

from django.db.models import QuerySet
from django.views import View
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request


class InTitleFilter(BaseFilterBackend):
    """The questions in title filter
    """
    in_title_param = 'intitle'

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Filter questions based on the title.

        :param request: The request.
        :param queryset: The queryset.
        :param view: The view.
        :return: The filtered queryset.
        """
        in_title = request.query_params.get(self.in_title_param)
        if in_title:
            queryset = queryset.filter(title_search=in_title)

        return queryset

    def get_schema_operation_parameters(self, view: View) -> typing.List[dict]:
        """Get the schema operation parameters.

        :param view: The view to get the parameters for.
        :return: The parameters.
        """
        return [
            {
                'name': self.in_title_param,
                'required': False,
                'in': 'query',
                'description': 'Include questions that contain the ',
                'schema': {
                    'type': 'string'
                },
            }
        ]
