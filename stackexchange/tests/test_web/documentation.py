"""API documentation tests
"""
import http

from django.test import TestCase
from django.urls import reverse


class APIDocumentationTestCase(TestCase):
    """Test API documentation.
    """
    def test_schema(self):
        """Test that the API schema can be loaded.
        """
        response = self.client.get(reverse('schema'), HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
