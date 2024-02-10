"""Base user test case.
"""
from stackexchange import enums, models
from ..base import BaseTestCase


class BaseUserTestCase(BaseTestCase):
    """Base user API test case
    """
    def assert_items_equal(self, response, model_class=models.User, obj_filter: str | dict = 'user_id',
                           multiple: bool = False, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if attributes is None:
            attributes = {
                'badge_counts.bronze': lambda x: models.UserBadge.objects.filter(
                    user=x, badge__badge_class=enums.BadgeClass.BRONZE.value
                ).count(),
                'badge_counts.silver': lambda x: models.UserBadge.objects.filter(
                    user=x, badge__badge_class=enums.BadgeClass.SILVER.value
                ).count(),
                'badge_counts.gold': lambda x: models.UserBadge.objects.filter(
                    user=x, badge__badge_class=enums.BadgeClass.GOLD.value
                ).count(),
                'is_employee': 'is_employee',
                'reputation': 'reputation',
                'creation_date': lambda x: x.creation_date.isoformat().replace('+00:00', 'Z'),
                'last_modified_date': lambda x: x.last_modified_date.isoformat().replace('+00:00', 'Z'),
                'location': 'location',
                'website_url': 'website_url',
                'display_name': 'display_name',
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)
