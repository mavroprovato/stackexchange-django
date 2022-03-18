"""Badges API retrieve testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import models
from stackexchange.tests import factories


class BadgeRetrieveTests(APITestCase):
    """Badges retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.BadgeFactory.create_batch(size=100)

    def test(self):
        """Test the badges detail endpoint.
        """
        badge = random.sample(list(models.Badge.objects.all()), 1)[0]
        response = self.client.get(reverse('badge-detail', kwargs={'pk': badge.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['items'][0]['badge_id'], badge.pk)

    def test_multiple(self):
        """Test the badges detail endpoint for multiple ids.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        response = self.client.get(reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual({row['badge_id'] for row in response.json()['items']}, {badge.pk for badge in badges})
