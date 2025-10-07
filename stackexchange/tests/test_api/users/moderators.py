"""Users API moderators testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums
from stackexchange.tests import base, factories


class UserModeratorsTests(base.BaseTestCase):
    """User view set moderators tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=10, is_moderator=random.choice([True, False]))
        badges = factories.BadgeFactory.create_batch(size=50)
        for _ in range(100):
            factories.UserBadgeFactory.create(user=random.choice(site_users), badge=random.choice(badges))

    def test(self):
        """Test users moderators endpoint
        """
        # Test that the list endpoint returns successfully
        response = self.client.get(reverse('api-user-moderators'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)

    def test_sort_by_reputation(self):
        """Test the users moderators endpoint sorted by user reputation.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-user-moderators'), data={'sort': 'reputation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_response(response)
            self.assert_items_sorted(response, 'reputation', order, enums.OrderingFieldType.INTEGER)

    def test_sort_by_creation(self):
        """Test the users moderators endpoint sorted by user creation date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-user-moderators'), data={'sort': 'creation', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_name(self):
        """Test the users moderators endpoint sorted by username.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-user-moderators'), data={'sort': 'name', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_response(response)
            self.assert_items_sorted(response, 'display_name', order, enums.OrderingFieldType.STRING)

    def test_sort_by_modified(self):
        """Test the users moderators endpoint sorted by user modification date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-user-moderators'), data={'sort': 'modified', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_response(response)
            self.assert_items_sorted(response, 'last_modified_date', order, enums.OrderingFieldType.DATE)

    def test_range_by_reputation(self):
        """Test the user list endpoint range by reputation.
        """
        min_value, max_value = self.generate_random_integers(max_value=500_000)
        response = self.client.get(
            reverse('api-user-moderators'), data={'sort': 'reputation', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)
        self.assert_items_in_range(response, 'reputation', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_range_by_creation(self):
        """Test the user list endpoint range by user creation date.
        """
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-user-moderators'),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_display_name(self):
        """Test the user list endpoint range by user display name.
        """
        min_value = 'k'
        max_value = 't'
        response = self.client.get(
            reverse('api-user-moderators'), data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)
        self.assert_items_in_range(response, 'name', enums.OrderingFieldType.STRING, min_value, max_value)

    def test_range_by_modified(self):
        """Test the user list endpoint range by user modified date.
        """
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(reverse('api-user-moderators'), data={
            'sort': 'modified', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)
        self.assert_items_in_range(response, 'last_modified_date', enums.OrderingFieldType.DATE, min_value)

    def test_date_range(self):
        """Test the user list endpoint by date range.
        """
        from_date, to_date = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-user-moderators'), data={'fromdate': from_date.isoformat(), 'todate': to_date.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, from_date, to_date)
