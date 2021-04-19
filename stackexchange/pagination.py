from rest_framework import pagination


class Pagination(pagination.PageNumberPagination):
    """The default pagination class
    """
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 100
