"""Users API moderators testing
"""
import datetime
import random
import unittest

from django.urls import reverse

from stackexchange import enums
from stackexchange.tests import factories
from .base import BaseUserTestCase


class UserModeratorsTests(BaseUserTestCase):
    """User view set moderators tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        site = factories.SiteFactory.create()
        site_users = factories.SiteUserFactory.create_batch(site=site, size=10)
        badges = factories.BadgeFactory.create_batch(size=50)
        for _ in range(100):
            factories.UserBadgeFactory.create(user=random.choice(site_users), badge=random.choice(badges))

    def test(self):
        """Test users list endpoint
        """
        # Test that the list endpoint returns successfully
        response = self.client.get(reverse('api-user-moderators'))
        self.assert_items_equal(response)

    def test_sort_by_reputation(self):
        """Test the user list sorted by user reputation.
        """
        response = self.client.get(reverse('api-user-moderators'), data={'sort': 'reputation', 'order': 'asc'})
        self.assert_sorted(response, 'reputation')

        response = self.client.get(reverse('api-user-moderators'), data={'sort': 'reputation', 'order': 'desc'})
        self.assert_sorted(response, 'reputation', reverse=True)

    def test_sort_by_creation(self):
        """Test the user list endpoint sorted by user creation date.
        """
        response = self.client.get(reverse('api-user-moderators'), data={'sort': 'creation', 'order': 'asc'})
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(reverse('api-user-moderators'), data={'sort': 'creation', 'order': 'desc'})
        self.assert_sorted(response, 'creation_date', reverse=True)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_sort_by_display_name(self):
        """Test the user list endpoint sorted by user display name.
        """
        response = self.client.get(reverse('api-user-moderators'), data={'sort': 'name', 'order': 'asc'})
        self.assert_sorted(response, 'display_name')

        response = self.client.get(reverse('user-moderators'), data={'sort': 'name', 'order': 'desc'})
        self.assert_sorted(response, 'display_name', reverse=True)

    def test_sort_by_modified(self):
        """Test the user list endpoint sorted by user modification date.
        """
        response = self.client.get(reverse('api-user-moderators'), data={'sort': 'modified', 'order': 'asc'})
        self.assert_sorted(response, 'last_modified_date')

        response = self.client.get(reverse('api-user-moderators'), data={'sort': 'modified', 'order': 'desc'})
        self.assert_sorted(response, 'last_modified_date', reverse=True)

    def test_range_by_reputation(self):
        """Test the user list endpoint range by reputation.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-user-moderators'), data={
            'sort': 'reputation', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'reputation', min_value, max_value)

    def test_range_by_creation(self):
        """Test the user list endpoint range by user creation date.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-user-moderators'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assert_range(response, 'creation_date', min_value, max_value)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_range_by_display_name(self):
        """Test the user list endpoint range by user display name.
        """
        min_value = 'k'
        max_value = 't'
        response = self.client.get(reverse('api-user-moderators'), data={
            'sort': 'name', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'display_name', min_value, max_value)

    def test_range_by_modified(self):
        """Test the user list endpoint range by user modified date.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-user-moderators'), data={
            'sort': 'modified', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assert_range(response, 'last_modified_date', min_value, max_value)

    def test_in_name(self):
        """Test the in name filter for the user list endpoint.
        """
        # Create a user that will surely be returned
        site_user = factories.SiteUserFactory.create(
            display_name='John Doe', reputation=enums.Privilege.ACCESS_TO_MODERATOR_TOOLS.reputation + 1)
        query = 'oh'
        response = self.client.get(reverse('api-user-moderators'), data={'inname': query})
        self.assert_in_string(response, 'display_name', query=query)
        self.assertIn(site_user.id, [int(row['user_id']) for row in response.json()['items']])
