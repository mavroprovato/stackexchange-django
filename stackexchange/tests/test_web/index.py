"""Index view tests
"""
import http

from django.test import TestCase
from django.urls import reverse

from .. import factories


class IndexViewTests(TestCase):
    """Index view tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        site_users = factories.SiteUserFactory.create_batch(size=10)
        for site_user in site_users:
            factories.QuestionFactory.create_batch(size=3, owner=site_user)

    def test(self):
        """Test the index view
        """
        response = self.client.get(reverse('web-index'), follow=True)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
