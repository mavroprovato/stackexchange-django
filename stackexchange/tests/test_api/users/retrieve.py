"""Users API retrieve testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import models
from stackexchange.tests import factories


class UserRetrieveTests(APITestCase):
    """User view set retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.UserFactory.create_batch(size=10)

    def test_detail(self):
        """Test the user detail endpoint.
        """
        # Test getting one user
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-detail', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['items'][0]['user_id'], user.pk)

    def test_detail_multiple(self):
        """Test the user detail endpoint for multiple ids.
        """
        # Test getting multiple users
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
