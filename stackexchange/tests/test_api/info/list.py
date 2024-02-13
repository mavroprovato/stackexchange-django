"""Info view set testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange.tests import factories


class InfoTests(APITestCase):
    """Info view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        cls.site = factories.SiteFactory.create()

    def test(self):
        """Test info list endpoint
        """
        response = self.client.get(reverse('api-info-list'), data={'site': self.site.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
