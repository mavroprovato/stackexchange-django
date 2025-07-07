"""Badges API list testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_badge_with_award_count_response(response)

    def test_sort_by_rank(self):
        """Test the badges list endpoint sorted by badge rank.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-badge-list'), data={'sort': 'rank', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_badge_with_award_count_response(response)
            self.assert_items_sorted(response, 'rank', order)

    def test_sort_by_name(self):
        """Test the badges list endpoint sorted by badge name.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-badge-list'), data={'sort': 'name', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_badge_with_award_count_response(response)
            self.assert_items_sorted(response, 'name', order)

    def test_sort_by_type(self):
        """Test the badges list endpoint sorted by badge type.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-badge-list'), data={'sort': 'type', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_badge_with_award_count_response(response)
            self.assert_items_sorted(response, 'badge_type', order)
