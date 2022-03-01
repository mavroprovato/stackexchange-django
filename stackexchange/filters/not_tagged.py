"""The questions tagged filter
"""
import typing

from django.db.models import QuerySet, Exists, OuterRef
from django.views import View
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request

from stackexchange import models


class NotTaggedFilter(BaseFilterBackend):
    """The questions not tagged filter
    """
    tagged_param = 'nottagged'

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Filter questions based on .

        :param request: The request.
        :param queryset: The queryset.
        :param view: The view.
        :return: The filtered queryset.
        """
        for tag_name in request.query_params.get(self.tagged_param, '').split(';'):
            tag_name = tag_name.strip()
            if tag_name:
                queryset = queryset.filter(~Exists(
                    models.PostTag.objects.filter(post=OuterRef('pk'), tag__name=tag_name)
                ))

        return queryset

    def get_schema_operation_parameters(self, view: View) -> typing.List[dict]:
        """Get the schema operation parameters.

        :param view: The view to get the parameters for.
        :return: The parameters.
        """
        return [
            {
                'name': self.tagged_param,
                'required': False,
                'in': 'query',
                'description': 'Include questions that are not tagged with the semicolon seperated list of tags',
                'schema': {
                    'type': 'string'
                },
            }
        ]
