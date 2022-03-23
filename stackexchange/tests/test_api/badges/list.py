"""Badges API list testing
"""
import unittest

from django.urls import reverse

from stackexchange import enums
from stackexchange.tests import factories
from .base import BaseBadgeTestCase


class BadgeListTests(BaseBadgeTestCase):
    """Badges view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.BadgeFactory.create_batch(size=100)

    def test(self):
        """Test badges list endpoint
        """
        response = self.client.get(reverse('badge-list'))
        self.assert_items_equal(response)

    def test_sort_by_rank(self):
        """Test the badges list sorted by badge rank.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'rank', 'order': 'asc'})
        self.assert_sorted(response, 'rank')

        response = self.client.get(reverse('badge-list'), data={'sort': 'rank', 'order': 'desc'})
        self.assert_sorted(response, 'rank', reverse=True)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_sort_by_name(self):
        """Test the badges list sorted by badge name.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'name', 'order': 'asc'})
        self.assert_sorted(response, 'name')

        response = self.client.get(reverse('badge-list'), data={'sort': 'name', 'order': 'desc'})
        self.assert_sorted(response, 'name', reverse=True)

    def test_sort_by_type(self):
        """Test the badges list sorted by badge type.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'type', 'order': 'asc'})
        self.assert_sorted(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value)

        response = self.client.get(reverse('badge-list'), data={'sort': 'type', 'order': 'desc'})
        self.assert_sorted(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value, reverse=True)
