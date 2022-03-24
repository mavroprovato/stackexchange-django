"""Base tag test case.
"""
from stackexchange import models
from ..base import BaseTestCase


class BaseTagTestCase(BaseTestCase):
    """Base API tag test case
    """
    def assert_items_equal(self, response, **kwargs):
        """Assert that the items returned by the response are the same as the database items.
        """
        return super().assert_items_equal(response, models.Tag, {'name': 'name'}, attributes={
            'name': 'name',
            'count': 'award_count',
        })
