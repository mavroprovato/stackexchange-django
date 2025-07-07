"""Badges API list testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange.tests import base, factories


class BadgeListTests(base.BaseTestCase):
    """Badges view set list tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=100)
        badges = factories.BadgeFactory.create_batch(size=25)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(site_users), badge=random.choice(badges))

    def test(self):
        """Test the badges list endpoint
        """
        response = self.client.get(reverse('api-badge-list'))
        self.assert_badge_with_award_count_response(response)
