"""Question view tests
"""
import http

from django.test import TestCase
from django.urls import reverse

from .. import factories


class QuestionViewTests(TestCase):
    """Question view tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=100)
        for user in users:
            factories.QuestionFactory.create_batch(size=3, owner=user)

    def test(self):
        """Test the question view
        """
        response = self.client.get(reverse('web-questions'), follow=True)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
