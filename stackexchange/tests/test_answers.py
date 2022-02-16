from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AnswerTests(APITestCase):
    """Answer view set tests
    """
    def test_list(self):
        """Test answer list endpoint
        """
        response = self.client.get(reverse('answer-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
