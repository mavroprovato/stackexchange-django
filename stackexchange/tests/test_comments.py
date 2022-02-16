from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CommentTests(APITestCase):
    """Comment view set tests
    """
    def test_list(self):
        """Test comment list endpoint
        """
        response = self.client.get(reverse('comment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
