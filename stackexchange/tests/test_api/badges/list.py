"""Badges API list testing
"""
import random

from django.urls import reverse

from stackexchange import enums
from stackexchange.tests import factories
from .base import BadgeWithAwardCountTestCase


class BadgeListTests(BadgeWithAwardCountTestCase):
    """Badges view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        users = factories.UserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=25)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(users), badge=random.choice(badges))

    def test(self):
        """Test badges list endpoint
        """
        response = self.client.get(reverse('badge-list'))
        self.assert_items_equal(response)

    def test_sort_by_rank(self):
        """Test the badges list endpoint sorted by badge rank.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'rank', 'order': 'asc'})
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value)

        response = self.client.get(reverse('badge-list'), data={'sort': 'rank', 'order': 'desc'})
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value, reverse=True)

    def test_sort_by_name(self):
        """Test the badges list endpoint sorted by badge name.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'name', 'order': 'asc'})
        self.assert_sorted(response, 'name', case_insensitive=True)

        response = self.client.get(reverse('badge-list'), data={'sort': 'name', 'order': 'desc'})
        self.assert_sorted(response, 'name', case_insensitive=True, reverse=True)

    def test_sort_by_type(self):
        """Test the badges list endpoint sorted by badge type.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'type', 'order': 'asc'})
        self.assert_sorted(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value)

        response = self.client.get(reverse('badge-list'), data={'sort': 'type', 'order': 'desc'})
        self.assert_sorted(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value, reverse=True)

    def test_range_by_rank(self):
        """Test the badges list endpoint range by badge rank.
        """
        min_value = enums.BadgeClass.SILVER
        response = self.client.get(reverse('badge-list'), data={
            'sort': 'rank', 'min': min_value.name.lower()
        })
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          min_value=min_value.value)
        max_value = enums.BadgeClass.SILVER
        response = self.client.get(reverse('badge-list'), data={
            'sort': 'rank', 'max': max_value.name.lower()
        })
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          max_value=max_value.value)

    def test_range_by_name(self):
        """Test the badges list endpoint range by badge name.
        """
        min_value = 'k'
        max_value = 't'
        response = self.client.get(reverse('badge-list'), data={'sort': 'name', 'min': min_value, 'max': max_value})
        self.assert_range(response, 'name', min_value, max_value)

    def test_range_by_type(self):
        """Test the badges list endpoint range by badge type.
        """
        min_value = enums.BadgeType.TAG_BASED
        response = self.client.get(reverse('badge-list'), data={
            'sort': 'type', 'min': min_value.name.lower()
        })
        self.assert_range(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value,
                          min_value=min_value.value)
        max_value = enums.BadgeType.NAMED
        response = self.client.get(reverse('badge-list'), data={
            'sort': 'type', 'max': max_value.name.lower()
        })
        self.assert_range(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value,
                          max_value=max_value.value)
