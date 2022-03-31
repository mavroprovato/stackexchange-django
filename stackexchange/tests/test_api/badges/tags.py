"""Badges view tags testing
"""
import random
import unittest

from django.urls import reverse

from stackexchange import enums
from stackexchange.tests import factories
from .base import BaseBadgeWithAwardCountTestCase


class BadgeTagsTests(BaseBadgeWithAwardCountTestCase):
    """Badges tags tests
    """
    @classmethod
    def setUpTestData(cls):
        users = factories.UserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=100)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(users), badge=random.choice(badges))

    def test(self):
        """Test badges tags endpoint
        """
        response = self.client.get(reverse('badge-tags'))
        self.assert_items_equal(response)
        self.assert_badge_type(response, enums.BadgeType.TAG_BASED)

    def test_sort_by_rank(self):
        """Test the badges tags endpoint sorted by badge rank.
        """
        response = self.client.get(reverse('badge-tags'), data={'sort': 'rank', 'order': 'asc'})
        self.assert_badge_type(response, enums.BadgeType.TAG_BASED)
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value)

        response = self.client.get(reverse('badge-tags'), data={'sort': 'rank', 'order': 'desc'})
        self.assert_badge_type(response, enums.BadgeType.TAG_BASED)
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value, reverse=True)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_sort_by_name(self):
        """Test the badges tags endpoint sorted by badge name.
        """
        response = self.client.get(reverse('badge-named'), data={'sort': 'name', 'order': 'asc'})
        self.assert_badge_type(response, enums.BadgeType.TAG_BASED)
        self.assert_sorted(response, 'name')

        response = self.client.get(reverse('badge-tags'), data={'sort': 'name', 'order': 'desc'})
        self.assert_badge_type(response, enums.BadgeType.TAG_BASED)
        self.assert_sorted(response, 'name', reverse=True)

    def test_range_by_rank(self):
        """Test the badges tags endpoint range by badge rank.
        """
        min_value = enums.BadgeClass.SILVER
        response = self.client.get(reverse('badge-tags'), data={
            'sort': 'rank', 'min': min_value.name.lower()
        })
        self.assert_badge_type(response, enums.BadgeType.TAG_BASED)
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          min_value=min_value.value)
        max_value = enums.BadgeClass.SILVER
        response = self.client.get(reverse('badge-tags'), data={
            'sort': 'rank', 'max': max_value.name.lower()
        })
        self.assert_badge_type(response, enums.BadgeType.TAG_BASED)
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          max_value=max_value.value)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_range_by_name(self):
        """Test the badges tags endpoint range by badge name.
        """
        min_value = 'b'
        max_value = 'x'
        response = self.client.get(reverse('badge-tags'), data={'sort': 'name', 'min': min_value, 'max': max_value})
        self.assert_badge_type(response, enums.BadgeType.TAG_BASED)
        self.assert_range(response, 'name', min_value, max_value)
