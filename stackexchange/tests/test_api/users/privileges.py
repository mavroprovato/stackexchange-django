"""Users API privileges testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums, models
from stackexchange.tests import factories


class UserPrivilegeTests(APITestCase):
    """User view set privileges tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.SiteUserFactory.create_batch(size=10)

    def test(self):
        """Test the user privileges endpoint.
        """
        site_user = random.sample(list(models.SiteUser.objects.all()), 1)[0]
        response = self.client.get(reverse('api-user-privileges', kwargs={'pk': site_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that the privileges are returned by ascending reputation
        self.assertListEqual([row['reputation'] for row in response.json()['items']],
                             sorted([row['reputation'] for row in response.json()['items']]))
        # Assert that the user has the correct privileges based on the reputation
        user_privileges = [privilege for privilege in enums.Privilege if privilege.reputation <= site_user.reputation]
        self.assertEqual(len(user_privileges), len(response.json()['items']))
        # Assert the privilege descriptions and short descriptions are correct
        self.assertListEqual([privilege.description for privilege in user_privileges],
                             [row['description'] for row in response.json()['items']])
        self.assertListEqual([privilege.name.replace('_', ' ').capitalize() for privilege in user_privileges],
                             [row['short_description'] for row in response.json()['items']])
