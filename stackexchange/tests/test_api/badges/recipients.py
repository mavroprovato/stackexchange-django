"""Badges view set recipients testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange.tests import factories


class BadgeRecipientTests(APITestCase):
    """Badges view set tests
    """
    @classmethod
    def setUpTestData(cls):
        users = factories.UserFactory.create_batch(size=10)
        # Award some badges to the users
        for user in users:
            factories.UserBadgeFactory.create_batch(size=random.randint(0, 20), user=user)

    def test(self):
        """Test badges recipients endpoint
        """
        response = self.client.get(reverse('badge-recipients'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
