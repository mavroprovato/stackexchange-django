"""Badges view set recipients detail testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from .base import BaseBadgeTestCase


class BadgeRecipientDetailTests(BaseBadgeTestCase):
    """Badges view set recipient detail tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        site = factories.SiteFactory.create()
        site_users = factories.SiteUserFactory.create_batch(site=site, size=10)
        badges = factories.BadgeFactory.create_batch(size=25)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(site_users), badge=random.choice(badges))

    def test(self):
        """Test badges recipients endpoint
        """
        badge = random.sample(list(models.Badge.objects.all()), 1)[0]
        response = self.client.get(reverse('api-badge-recipients-detail', kwargs={'pk': badge.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test badges recipients endpoint for multiple ids
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        response = self.client.get(
            reverse('api-badge-recipients-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}))
        self.assert_items_equal(response)

    def test_date_range(self):
        """Test the badges recipients endpoint date range.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        from_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-badge-recipients-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}), data={
                'fromdate': from_value, 'todate': to_value
            }
        )
        self.assert_range(response, 'creation_date', from_value, to_value)
