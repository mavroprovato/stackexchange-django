from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class QuestionTests(APITestCase):
    """Question view set tests
    """
    def test_list(self):
        """Test question list endpoint
        """
        response = self.client.get(reverse('question-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_answers(self):
        """Test question with no answer endpoint
        """
        response = self.client.get(reverse('question-no-answers'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
