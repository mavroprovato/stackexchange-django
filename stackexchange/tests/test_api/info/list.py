"""Info view set testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class InfoTests(APITestCase):
    """Info view set list tests
    """
    def test(self):
        """Test info list endpoint
        """
        response = self.client.get(reverse('info-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
