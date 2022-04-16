"""Index view tests
"""
import http

from django.test import TestCase
from django.urls import reverse


class IndexViewTests(TestCase):
    """Index view tests
    """
    def test(self):
        """Test the index view
        """
        response = self.client.get(reverse('web-index'), follow=True)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
