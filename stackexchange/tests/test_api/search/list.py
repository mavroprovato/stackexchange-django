"""Search view set testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SearchTests(APITestCase):
    """Search view set tests
    """
    def test(self):
        """Test search list endpoint
        """
        response = self.client.get(reverse('search-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
