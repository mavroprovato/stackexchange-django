"""Badges view set recipients testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..test_data import setup_test_data


class BadgeRecipientTests(APITestCase):
    """Badges view set tests
    """
    @classmethod
    def setUpTestData(cls):
        setup_test_data()

    def test(self):
        """Test badges recipients endpoint
        """
        response = self.client.get(reverse('badge-recipients'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
