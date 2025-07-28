"""Badges API tags testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums
from stackexchange.tests import base, factories


class BadgeTagsTests(base.BaseTestCase):
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
        """Test the badges named endpoint
        """
        response = self.client.get(reverse('api-badge-tags'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_badge_with_award_count_response(response)

    def test_sort_by_rank(self):
        """Test the badges named endpoint sorted by badge rank.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-badge-tags'), data={'sort': 'rank', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_badge_with_award_count_response(response)
            self.assert_items_sorted(response, 'rank', order, field_type=enums.OrderingFieldType.RANK)

    def test_sort_by_name(self):
        """Test the badges named endpoint sorted by badge name.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-badge-tags'), data={'sort': 'name', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_badge_with_award_count_response(response)
            self.assert_items_sorted(response, 'name', order, enums.OrderingFieldType.STRING)

    def test_range_by_rank(self):
        """Test the badges named endpoint range by badge rank.
        """
        min_value = enums.BadgeRank.SILVER
        response = self.client.get(reverse('api-badge-tags'), data={
            'sort': 'rank', 'min': min_value.value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_badge_with_award_count_response(response)
        self.assert_items_in_range(response, 'rank', min_value=min_value, field_type=enums.OrderingFieldType.RANK)

        max_value = enums.BadgeRank.SILVER
        response = self.client.get(reverse('api-badge-tags'), data={
            'sort': 'rank', 'max': max_value.value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_badge_with_award_count_response(response)
        self.assert_items_in_range(response, 'rank', max_value=max_value, field_type=enums.OrderingFieldType.RANK)

    def test_range_by_name(self):
        """Test the badges named endpoint range by badge name.
        """
        min_value = 'k'
        max_value = 't'
        response = self.client.get(
            reverse('api-badge-tags'), data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_badge_with_award_count_response(response)
        self.assert_items_in_range(response, 'name', enums.OrderingFieldType.STRING, min_value, max_value)
