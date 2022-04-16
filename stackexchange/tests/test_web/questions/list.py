"""Question list tests
"""
import http

from django.test import TestCase
from django.urls import reverse

from stackexchange.tests import factories


class QuestionListTests(TestCase):
    """Question list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.QuestionFactory.create_batch(size=100)

    def test(self):
        """Test the question list
        """
        response = self.client.get(reverse('web-question-list'), follow=True)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
