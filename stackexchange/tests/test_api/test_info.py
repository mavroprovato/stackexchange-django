"""Badges view set testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class InfoTests(APITestCase):
    """Badges view set tests
    """
    def test_list(self):
        """Test badges list endpoint
        """
        response = self.client.get(reverse('info-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
