"""Users API testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserTests(APITestCase):
    """Users view set tests
    """
    def test_list(self):
        """Test users list endpoint
        """
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
