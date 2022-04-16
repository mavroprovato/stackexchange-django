"""Question view tests
"""
import http

from django.test import TestCase
from django.urls import reverse


class QuestionViewTests(TestCase):
    """Question view tests
    """
    def test(self):
        """Test the question view
        """
        response = self.client.get(reverse('web-questions'), follow=True)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
