from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class BadgesTests(APITestCase):
    """Badges view set tests
    """
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
