"""Badges view set recipients testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange.tests import factories
from .base import BaseBadgeTestCase


class BadgeRecipientTests(BaseBadgeTestCase):
    """Badges view set tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=25)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(users), badge=random.choice(badges))

    def test(self):
        """Test badges recipients endpoint
        """
        response = self.client.get(reverse('badge-recipients'))
        self.assert_items_equal(response)

    def test_date_range(self):
        """Test the badges recipients endpoint date range.
        """
        from_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('badge-recipients'), data={
            'fromdate': from_value, 'todate': to_value
        })
        self.assert_range(response, 'creation_date', from_value, to_value)
