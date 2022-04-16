"""Tag view tests
"""
import http

from django.test import TestCase
from django.urls import reverse

from .. import factories


class TagViewTests(TestCase):
    """Tag view tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.TagFactory.create_batch(size=100)

    def test(self):
        """Test the question view
        """
        response = self.client.get(reverse('web-tags'), follow=True)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
