"""Base badge test case.
"""
import typing

from stackexchange import enums, models
from ..base import BaseTestCase


class BaseBadgeTestCase(BaseTestCase):
    """Base API badge test case
    """
    def assert_items_equal(self, response, model_class: typing.ClassVar = models.Badge,
                           obj_filter: typing.Union[str, dict] = 'badge_id',
                           multiple: bool = False, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if attributes is None:
            attributes = {
                'badge_type': lambda x: enums.BadgeType(x.badge_type).name.lower(),
                'rank': lambda x: enums.BadgeClass(x.badge_class).name.lower(),
                'name': 'name',
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)

    def assert_badge_type(self, response, badge_type: enums.BadgeType):
        """Assert that all badges in the response are of the specified type.

        :param response: The response.
        :param badge_type: The badge type to expect.
        """
        self.assertTrue(all(row['badge_type'] == badge_type.name.lower() for row in response.json()['items']))


class BadgeWithAwardCountTestCase(BaseBadgeTestCase):
    """Base API badge test case with award count
    """
    def assert_items_equal(self, response, model_class: typing.ClassVar = models.Badge,
                           obj_filter: typing.Union[str, dict] = 'badge_id',
                           multiple: bool = False, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if attributes is None:
            attributes = {
                'badge_type': lambda x: enums.BadgeType(x.badge_type).name.lower(),
                'award_count': lambda x: models.UserBadge.objects.filter(badge=x).count(),
                'rank': lambda x: enums.BadgeClass(x.badge_class).name.lower(),
                'name': 'name',
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)


class UserBadgeTestCase(BaseBadgeTestCase):
    """Base API user badge test case
    """
    def assert_items_equal(self, response, model_class: typing.ClassVar = models.UserBadge,
                           obj_filter: typing.Union[str, dict] = None,
                           multiple: bool = True, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if obj_filter is None:
            obj_filter = {'user': 'user.user_id', 'badge__name': 'name'}
        if attributes is None:
            attributes = {
                'badge_type': lambda x: enums.BadgeType(x.badge.badge_type).name.lower(),
                'rank': lambda x: enums.BadgeClass(x.badge.badge_class).name.lower(),
                'name': lambda x: x.badge.name,
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)
