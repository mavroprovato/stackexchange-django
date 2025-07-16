"""Badges view set recipients testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange.tests import base, factories


class BadgeRecipientTests(base.BaseTestCase):
    """Badges view set tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=25)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(site_users), badge=random.choice(badges))

    def test(self):
        """Test badges recipients endpoint
        """
        response = self.client.get(reverse('api-badge-recipients'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_badge_with_recipient_response(response)
