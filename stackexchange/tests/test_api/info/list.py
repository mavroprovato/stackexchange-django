"""Info view set testing
"""
from django.urls import reverse
from rest_framework import status

from stackexchange.tests.base import BaseTestCase


class InfoTests(BaseTestCase):
    """Info view set list tests
    """
    def test(self):
        """Test info list endpoint
        """
        response = self.client.get(reverse('api-info-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
