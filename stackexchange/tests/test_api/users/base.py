"""Base user test case.
"""
from stackexchange import models
from ..base import BaseTestCase


class BaseUserTestCase(BaseTestCase):
    """Base API test case
    """
    def assert_items_equal(self, response, **kwargs):
        """Assert that the items returned by the response are the same as the database items.

        :param response: The response.
        """
        return super().assert_items_equal(response, models.User, 'user_id', attributes={
            'is_employee': 'is_employee',
            'reputation': 'reputation',
            'creation_date': lambda x: x.isoformat().replace('+00:00', 'Z'),
            'last_modified_date': lambda x: x.isoformat().replace('+00:00', 'Z'),
            'location': 'location',
            'website_url': 'website_url',
            'display_name': 'display_name',
        })
