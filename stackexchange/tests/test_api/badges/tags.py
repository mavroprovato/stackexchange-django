"""Badges view tags testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums, models
from stackexchange.tests import factories


class BadgeTagsTests(APITestCase):
    """Badges view set tag tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.BadgeFactory.create_batch(size=100)

    def test_tags(self):
        """Test badges tags endpoint
        """
        response = self.client.get(reverse('badge-tags'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the badge information returned is correct
        for row in response.json()['items']:
            badge = models.Badge.objects.get(pk=row['badge_id'])
            self.assertEqual(row['badge_type'], 'tag_based')
            self.assertEqual(row['rank'], enums.BadgeClass(badge.badge_class).name.lower())
            self.assertEqual(row['name'], badge.name)

    def test_tags_sort_by_rank(self):
        """Test the badges tags sorted by badge rank.
        """
        response = self.client.get(reverse('badge-tags'), data={'sort': 'rank', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_ranks = [enums.BadgeClass[row['rank'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_ranks, sorted(badge_ranks))

        response = self.client.get(reverse('badge-tags'), data={'sort': 'rank', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_ranks = [enums.BadgeClass[row['rank'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_ranks, sorted(badge_ranks, reverse=True))

    def test_tags_sort_by_name(self):
        """Test the badges tags sorted by badge name.
        """
        response = self.client.get(reverse('badge-tags'), data={'sort': 'name', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_names = [row['name'].lower() for row in response.json()['items']]
        self.assertListEqual(badge_names, sorted(badge_names))

        response = self.client.get(reverse('badge-tags'), data={'sort': 'name', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_names = [row['name'].lower() for row in response.json()['items']]
        self.assertListEqual(badge_names, sorted(badge_names, reverse=True))

    def test_tags_sort_by_type(self):
        """Test the badges tags sorted by badge type.
        """
        response = self.client.get(reverse('badge-tags'), data={'sort': 'type', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [enums.BadgeType[row['badge_type'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types))

        response = self.client.get(reverse('badge-tags'), data={'sort': 'type', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [enums.BadgeType[row['badge_type'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types, reverse=True))
