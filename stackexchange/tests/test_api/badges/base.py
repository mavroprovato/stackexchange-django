"""Base badge test case.
"""
from stackexchange import enums, models
from ..base import BaseTestCase


class BaseBadgeTestCase(BaseTestCase):
    """Base API test case
    """
    def assert_items_equal(self, response, **kwargs):
        """Assert that the items returned by the response are the same as the database items.
        """
        return super().assert_items_equal(response, models.Badge, 'badge_id', attributes={
            'badge_type': lambda x: enums.BadgeType(x.badge_type).name.lower(),
            'rank': lambda x: enums.BadgeClass(x.badge_class).name.lower(),
            'name': 'name',
        })

    def assert_badge_type(self, response, badge_type: enums.BadgeType):
        """Assert that all badges in the response are of the specified type.

        :param response:
        :param badge_type:
        :return:
        """
        self.assertTrue(all(row['badge_type'] == badge_type.name.lower() for row in response.json()['items']))
