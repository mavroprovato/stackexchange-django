"""Users API retrieve testing
"""
import datetime
import random
import unittest

from django.urls import reverse
from rest_framework import status

from stackexchange import models
from stackexchange.tests import factories
from .base import BaseUserTestCase


class UserRetrieveTests(BaseUserTestCase):
    """User view set retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        users = factories.UserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=50)
        for _ in range(100):
            factories.UserBadgeFactory.create(user=random.choice(users), badge=random.choice(badges))

    def test(self):
        """Test the user detail endpoint.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': user.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the user detail endpoint for multiple ids.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}))
        self.assert_items_equal(response)

    def test_sort_by_reputation(self):
        """Test the user detail endpoint sorted by user reputation.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'reputation', 'order': 'asc'})
        self.assert_sorted(response, 'reputation')

        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'reputation', 'order': 'desc'})
        self.assert_sorted(response, 'reputation', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the user detail sorted by user creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'creation', 'order': 'asc'})
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'creation', 'order': 'desc'})
        self.assert_sorted(response, 'creation_date', reverse=True)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_sort_by_display_name(self):
        """Test the user detail sorted by user display name.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'name', 'order': 'asc'})
        self.assert_sorted(response, 'display_name')

        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'name', 'order': 'desc'})
        self.assert_sorted(response, 'display_name', reverse=True)

    def test_sort_by_modified_date(self):
        """Test the user detail sorted by user modification date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'modified', 'order': 'asc'})
        self.assert_sorted(response, 'last_modified_date')

        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'modified', 'order': 'desc'})
        self.assert_sorted(response, 'last_modified_date', reverse=True)

    def test_range_by_reputation(self):
        """Test the user detail range by reputation.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'reputation', 'min': min_value, 'max': max_value})
        self.assert_range(response, 'reputation', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the user detail range by user creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'creation', 'min': min_value, 'max': max_value})
        self.assert_range(response, 'creation_date', min_value, max_value)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_range_by_display_name(self):
        """Test the user detail sorted by user display name.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = 'k'
        max_value = 't'
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'name', 'min': min_value, 'max': max_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_range(response, 'display_name', min_value, max_value)

    def test_range_by_modification_date(self):
        """Test the user detail range by user modification date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'modified', 'min': min_value, 'max': max_value})
        self.assert_range(response, 'last_modified_date', min_value, max_value)
