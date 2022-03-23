"""Users API list testing
"""
import datetime
import unittest

from django.urls import reverse
from rest_framework import status

from stackexchange.tests import factories
from .base import BaseUserTestCase


class UserListTests(BaseUserTestCase):
    """User view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.UserFactory.create_batch(size=10)

    def test(self):
        """Test users list endpoint
        """
        response = self.client.get(reverse('user-list'))
        # Test that the list endpoint returns successfully
        self.assert_items_equal(response)

    def test_sort_by_reputation(self):
        """Test the user list sorted by user reputation.
        """
        response = self.client.get(reverse('user-list'), data={'sort': 'reputation', 'order': 'asc'})
        self.assert_sorted(response, 'reputation')

        response = self.client.get(reverse('user-list'), data={'sort': 'reputation', 'order': 'desc'})
        self.assert_sorted(response, 'reputation', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the user list endpoint sorted by user creation date.
        """
        response = self.client.get(reverse('user-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(reverse('user-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assert_sorted(response, 'creation_date', reverse=True)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_sort_by_display_name(self):
        """Test the user list endpoint sorted by user display name.
        """
        response = self.client.get(reverse('user-list'), data={'sort': 'name', 'order': 'asc'})
        self.assert_sorted(response, 'display_name')

        response = self.client.get(reverse('user-list'), data={'sort': 'name', 'order': 'desc'})
        self.assert_sorted(response, 'display_name', reverse=True)

    def test_sort_by_modification_date(self):
        """Test the user list endpoint sorted by user modification date.
        """
        response = self.client.get(reverse('user-list'), data={'sort': 'modified', 'order': 'asc'})
        self.assert_sorted(response, 'last_modified_date')

        response = self.client.get(reverse('user-list'), data={'sort': 'modified', 'order': 'desc'})
        self.assert_sorted(response, 'last_modified_date', reverse=True)

    def test_range_by_reputation(self):
        """Test the user list endpoint range by reputation.
        """
        min_value = 10
        response = self.client.get(reverse('user-list'), data={'sort': 'reputation', 'min': min_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['reputation'] >= min_value for row in response.json()['items']))

        max_value = 1000
        response = self.client.get(reverse('user-list'), data={'sort': 'reputation', 'max': max_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['reputation'] <= max_value for row in response.json()['items']))

    def test_range_by_creation_date(self):
        """Test the user list endpoint range by user creation date.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        response = self.client.get(reverse('user-list'), data={'sort': 'creation', 'min': min_value.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['creation_date'] >= min_value.isoformat() for row in response.json()['items']))

        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('user-list'), data={'sort': 'creation', 'max': max_value.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['creation_date'] <= max_value.isoformat() for row in response.json()['items']))

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_range_by_display_name(self):
        """Test the user list endpoint range by user display name.
        """
        min_value = 'b'
        response = self.client.get(reverse('user-list'), data={'sort': 'name', 'min': min_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['display_name'] >= min_value for row in response.json()['items']))

        max_value = 'x'
        response = self.client.get(reverse('user-list'), data={'sort': 'name', 'max': max_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['display_name'] <= max_value for row in response.json()['items']))

    def test_range_by_modification_date(self):
        """Test the user list endpoint range by user modified date.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        response = self.client.get(reverse('user-list'), data={'sort': 'modified', 'min': min_value.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['last_modified_date'] >= min_value.isoformat() for row in response.json()['items']))

        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('user-list'), data={'sort': 'modified', 'max': max_value.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['last_modified_date'] <= max_value.isoformat() for row in response.json()['items']))

    def test_in_name(self):
        """Test the in name filter for users.
        """
        # Create a user that will surely be returned
        user = factories.UserFactory.create(display_name='John Doe')
        response = self.client.get(reverse('user-list'), data={'inname': 'oh'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that all users contain the string in their display name
        self.assertTrue(all('oh' in row['display_name'] for row in response.json()['items']))
        # Assert that the user was returned
        self.assertIn(user.id, [int(row['user_id']) for row in response.json()['items']])
