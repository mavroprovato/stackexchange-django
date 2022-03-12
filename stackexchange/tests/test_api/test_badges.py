"""Badges view set testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .. import factories


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

    def test_named(self):
        """Test badges named endpoint
        """
        response = self.client.get(reverse('badge-named'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
