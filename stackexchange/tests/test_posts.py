from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PostTests(APITestCase):
    """Post view set tests
    """
    def test_list(self):
        """Test post list endpoint
        """
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
