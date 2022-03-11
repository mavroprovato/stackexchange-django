"""Users API testing
"""
import dateutil.parser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .. import factories
from stackexchange import models


class UserTests(APITestCase):
    """Users view set tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.UserFactory.create_batch(size=100)

    def test_list(self):
        """Test users list endpoint
        """
        # Test that the list endpoint returns successfully
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user information returned is correct
        for row in response.json()['items']:
            user = models.User.objects.get(pk=row['user_id'])
            self.assertEqual(row['is_employee'], user.is_employee)
            self.assertEqual(row['reputation'], user.reputation)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), user.creation_date)
            self.assertEqual(row['location'], user.location)
            self.assertEqual(row['website_url'], user.website_url)
            self.assertEqual(row['display_name'], user.display_name)
