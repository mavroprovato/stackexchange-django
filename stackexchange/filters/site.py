"""The site filter
"""
from django.db.models import QuerySet
from django.views import View
from rest_framework.exceptions import APIException
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request

from stackexchange import models


class SiteFilter(BaseFilterBackend):
    """The questions in title filter
    """
    site_param = 'site'

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        """Filter entities based on site.

        :param request: The request.
        :param queryset: The queryset.
        :param view: The view.
        :return: The filtered queryset.
        """
        site_param = request.query_params.get(self.site_param)
        if site_param:
            try:
                site = models.Site.objects.get(name=site_param)
            except models.Site.DoesNotExist as exc:
                raise APIException(detail=f"No site found for name {site_param}", code=400) from exc

            queryset = queryset.filter(pk=site.pk)
        else:
            raise APIException(detail=f"{self.site_param} is required", code=400)

        return queryset

    def get_schema_operation_parameters(self, view: View) -> list[dict]:
        """Get the schema operation parameters.

        :param view: The view to get the parameters for.
        :return: The parameters.
        """
        return [
            {
                'name': self.site_param,
                'required': True,
                'in': 'query',
                'description': 'The site name',
                'schema': {'type': 'string'},
            }
        ]
