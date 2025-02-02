"""Pagination classes
"""
import collections.abc

from django.core.paginator import InvalidPage, PageNotAnInteger, EmptyPage
from django.views import View
from django.utils.translation import gettext_lazy as _
from rest_framework import pagination
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange.exceptions import ValidationError


class Page(collections.abc.Sequence):
    """The default page implementation.
    """
    def __init__(self, object_list: collections.abc.Collection, page_size: int, paginator) -> None:
        """Create the page.

        :param object_list: The object list.
        :param page_size: The page size.
        :param paginator: The paginator.
        """
        self.object_list = object_list
        # The object_list is converted to a list so that if it was a QuerySet it won't be a database hit per
        # __getitem__.
        if not isinstance(self.object_list, list):
            self.object_list = list(self.object_list)
        self.page_size = page_size
        self.paginator = paginator

    def __getitem__(self, index: int | slice) -> object:
        """Get the item at the specified index.

        :param index: The index.
        :return: The item.
        """
        if not isinstance(index, (int, slice)):
            raise TypeError(f'Page indices must be integers or slices, not {type(index).__name__}.')

        return self.object_list[index]

    def __len__(self) -> int:
        """Get the actual number of items for the page.

        :return: The actual number of items for the page.
        """
        return len(self.object_list[:self.page_size])

    def has_next(self) -> bool:
        """Return true if there is a next page.

        :return: true if there is a next page.
        """
        return len(self.object_list) > self.page_size


class Paginator:
    """The default paginator.
    """
    def __init__(self, queryset: collections.abc.Collection, page_size: int) -> None:
        """Create the paginator.

        :param queryset: The queryset to paginate.
        :param page_size: The page size.
        """
        self.queryset = queryset
        self.page_size = page_size

    def page(self, number: str) -> Page:
        """Return a Page object for the given 1-based page number.

        :param number: The page number as a string.
        :return: The page object.
        """
        number = self.validate_number(number)
        bottom = (number - 1) * self.page_size
        top = bottom + self.page_size

        return Page(self.queryset[bottom:top+1], self.page_size, self)

    @staticmethod
    def validate_number(number: str) -> int:
        """Validate the given 1-based page number.

        :param number: The given number.
        :return: The page number as an integer.
        """
        try:
            if isinstance(number, float) and not number.is_integer():
                raise ValueError
            number = int(number)
        except (TypeError, ValueError) as exception:
            raise PageNotAnInteger(_('That page number is not an integer')) from exception
        if number < 1:
            raise EmptyPage(_('That page number is less than 1'))

        return number


class Pagination(pagination.PageNumberPagination):
    """The default pagination class
    """
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 100
    django_paginator_class = Paginator

    def __init__(self) -> None:
        """Create the pagination object.
        """
        self.page = None

    def paginate_queryset(
            self, queryset: collections.abc.Collection, request: Request, view: View = None
    ) -> collections.abc.Collection:
        """Paginate a queryset if required, either returning a page object, or `None` if pagination is not configured
        for this view.

        :param queryset: The queryset.
        :param request: The request.
        :param view: The view.
        :return: The page object if pagination is required.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return queryset
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exception:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exception)
            )
            raise NotFound(msg) from exception

        return list(self.page)[:page_size]

    def get_paginated_response(self, data: collections.abc.Iterable) -> Response:
        """Return the paginated response.

        :param data: The data.
        :return: The paginated response.
        """
        return Response(collections.OrderedDict([
            ('items', data),
            ('has_more', self.page.has_next()),
        ]))

    def get_page_size(self, request: Request) -> int | None:
        """Return the page size. Raise a ValidationError if the page size is invalid.

        :param request: The request.
        :return: The page size.
        """
        page_size = self.max_page_size
        if self.page_size_query_param in request.query_params:
            value = request.query_params[self.page_size_query_param]
            if value:
                try:
                    page_size = int(value)
                    if page_size > self.max_page_size:
                        raise ValidationError('pagesize')
                except ValueError:
                    raise ValidationError('pagesize')

        return page_size
