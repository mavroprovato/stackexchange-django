"""Users API list testing
"""
import random

from django.urls import reverse
import dateutil.parser
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import factories
from stackexchange.tests.base import BaseTestCase


class UserListTests(BaseTestCase):
    """User view set list tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=50)
        for _ in range(100):
            factories.UserBadgeFactory.create(user=random.choice(site_users), badge=random.choice(badges))

    def test(self):
        """Test users list endpoint
        """
        # Test that the list endpoint returns successfully
        response = self.client.get(reverse('api-user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for item in response.json()['items']:
            user = models.SiteUser.objects.get(id=item['user_id'])
            self.assertEqual(item['badge_counts']['bronze'], models.UserBadge.objects.filter(
                    user=user, badge__badge_class=enums.BadgeClass.BRONZE.value
            ).count())
            self.assertEqual(item['badge_counts']['silver'], models.UserBadge.objects.filter(
                    user=user, badge__badge_class=enums.BadgeClass.SILVER.value
            ).count())
            self.assertEqual(item['badge_counts']['gold'], models.UserBadge.objects.filter(
                    user=user, badge__badge_class=enums.BadgeClass.GOLD.value
            ).count())
            self.assertEqual(item['reputation'], user.reputation)
            self.assertEqual(item['location'], user.location)
            self.assertEqual(item['website_url'], user.website_url)
            self.assertEqual(item['display_name'], user.display_name)
            self.assertEqual(dateutil.parser.parse(item['creation_date']), user.creation_date)
            self.assertEqual(dateutil.parser.parse(item['last_modified_date']), user.last_modified_date)
