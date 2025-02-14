"""Badges view tags testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import enums, models
from stackexchange.tests import factories
from .base import BadgeWithAwardCountTestCase


class BadgeTagsTests(BadgeWithAwardCountTestCase):
    """Badges tags tests
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

    def assert_items_equal(self, response, model_class=models.Badge, obj_filter: str | dict = 'badge_id',
                           multiple: bool = False, attributes: dict = None):
        """Overridden in order to validate that we only get tag named badges
        """
        super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)
        self.assertTrue(
            all(row['badge_type'] == enums.BadgeType.TAG_BASED.name.lower() for row in response.json()['items']))

    def test(self):
        """Test badges tags endpoint
        """
        response = self.client.get(reverse('api-badge-tags'))
        self.assert_items_equal(response)

    def test_sort_by_rank(self):
        """Test the badges tags endpoint sorted by badge rank.
        """
        response = self.client.get(reverse('api-badge-tags'), data={'sort': 'rank', 'order': 'asc'})
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value)

        response = self.client.get(reverse('api-badge-tags'), data={'sort': 'rank', 'order': 'desc'})
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value, reverse=True)

    def test_sort_by_name(self):
        """Test the badges tags endpoint sorted by badge name.
        """
        response = self.client.get(reverse('api-badge-tags'), data={'sort': 'name', 'order': 'asc'})
        self.assert_sorted(response, 'name', case_insensitive=True)

        response = self.client.get(reverse('api-badge-tags'), data={'sort': 'name', 'order': 'desc'})
        self.assert_sorted(response, 'name', case_insensitive=True, reverse=True)

    def test_range_by_rank(self):
        """Test the badges tags endpoint range by badge rank.
        """
        min_value = enums.BadgeClass.SILVER
        response = self.client.get(reverse('api-badge-tags'), data={
            'sort': 'rank', 'min': min_value.name.lower()
        })
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          min_value=min_value.value)
        max_value = enums.BadgeClass.SILVER
        response = self.client.get(reverse('api-badge-tags'), data={
            'sort': 'rank', 'max': max_value.name.lower()
        })
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          max_value=max_value.value)

    def test_range_by_name(self):
        """Test the badges tags endpoint range by badge name.
        """
        min_value = 'k'
        max_value = 't'
        response = self.client.get(reverse('api-badge-tags'), data={'sort': 'name', 'min': min_value, 'max': max_value})
        self.assert_range(response, 'name', min_value, max_value)

    def test_date_range(self):
        """Test the badges tags endpoint date range.
        """
        from_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-badge-tags'), data={
            'fromdate': from_value, 'todate': to_value
        })
        self.assert_range(response, 'creation_date', from_value, to_value)
