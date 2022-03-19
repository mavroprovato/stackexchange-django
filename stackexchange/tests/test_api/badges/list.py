"""Badges API list testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums, models
from stackexchange.tests import factories


class BadgeListTests(APITestCase):
    """Badges view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.BadgeFactory.create_batch(size=100)

    def test(self):
        """Test badges list endpoint
        """
        response = self.client.get(reverse('badge-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the badge information returned is correct
        for row in response.json()['items']:
            badge = models.Badge.objects.get(pk=row['badge_id'])
            self.assertEqual(row['badge_type'], enums.BadgeType(badge.badge_type).name.lower())
            self.assertEqual(row['rank'], enums.BadgeClass(badge.badge_class).name.lower())
            self.assertEqual(row['name'], badge.name)

    def test_sort_by_rank(self):
        """Test the badges list sorted by badge rank.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'rank', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_ranks = [enums.BadgeClass[row['rank'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_ranks, sorted(badge_ranks))

        response = self.client.get(reverse('badge-list'), data={'sort': 'rank', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_ranks = [enums.BadgeClass[row['rank'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_ranks, sorted(badge_ranks, reverse=True))

    def test_sort_by_name(self):
        """Test the badges list sorted by badge name.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'name', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_names = [row['name'].lower() for row in response.json()['items']]
        self.assertListEqual(badge_names, sorted(badge_names))

        response = self.client.get(reverse('badge-list'), data={'sort': 'name', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_names = [row['name'].lower() for row in response.json()['items']]
        self.assertListEqual(badge_names, sorted(badge_names, reverse=True))

    def test_sort_by_type(self):
        """Test the badges list sorted by badge type.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'type', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [enums.BadgeType[row['badge_type'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types))

        response = self.client.get(reverse('badge-list'), data={'sort': 'type', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [enums.BadgeType[row['badge_type'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types, reverse=True))