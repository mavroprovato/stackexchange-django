"""The questions tagged filter
"""
import functools
import operator

from django.db.models import QuerySet, Exists, OuterRef
from django.views import View
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request

from stackexchange import models


class TaggedFilter(BaseFilterBackend):
    """The questions tagged filter
    """
    param_name = 'tagged'

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Filter questions that are tagged with any of the provided tags. The tags are a semicolon separated list that
        is provided by the `TaggedFilter.param_name` parameter.

        :param request: The request.
        :param queryset: The queryset.
        :param view: The view.
        :return: The filtered queryset.
        """
        conditions = [
            Exists(
                models.PostTag.objects.filter(post=OuterRef('pk'), tag__name=tag_name.strip())
            )
            for tag_name in request.query_params.get(self.param_name, '').split(';') if tag_name.strip()
        ]
        if conditions:
            queryset = queryset.filter(functools.reduce(operator.and_, conditions))

        return queryset

    def get_schema_operation_parameters(self, view: View) -> list[dict]:
        """Get the schema operation parameters.

        :param view: The view to get the parameters for.
        :return: The parameters.
        """
        return [
            {
                'name': self.param_name,
                'required': False,
                'in': 'query',
                'description': 'Include questions that are tagged with any of the semicolon seperated list of tags',
                'schema': {
                    'type': 'string'
                },
            }
        ]
