"""Badges view set testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .. import factories
from stackexchange import enums, models


class BadgeTests(APITestCase):
    """Badges view set tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.BadgeFactory.create_batch(size=100)

    def test_list(self):
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

    def test_named(self):
        """Test badges named endpoint
        """
        response = self.client.get(reverse('badge-named'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the badge information returned is correct
        for row in response.json()['items']:
            badge = models.Badge.objects.get(pk=row['badge_id'])
            self.assertEqual(row['badge_type'], 'named')
            self.assertEqual(row['rank'], enums.BadgeClass(badge.badge_class).name.lower())
            self.assertEqual(row['name'], badge.name)

    def test_recipients(self):
        """Test badges recipients endpoint
        """
        response = self.client.get(reverse('badge-recipients'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
