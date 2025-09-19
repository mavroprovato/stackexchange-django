"""User view set detail testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class UserListTests(base.BaseTestCase):
    """User view set list tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=50)
        for _ in range(100):
            factories.UserBadgeFactory.create(user=random.choice(site_users), badge=random.choice(badges))

    def test(self):
        """Test the user detail endpoint.
        """
        user = random.sample(list(models.SiteUser.objects.all()), 1)[0]
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)

    def test_multiple(self):
        """Test the user detail endpoint for multiple ids.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)

    def test_sort_by_reputation(self):
        """Test the user list endpoint sorted by user reputation.
        """
        for order in enums.OrderingDirection:
            users = random.sample(list(models.SiteUser.objects.all()), 3)
            response = self.client.get(
                reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                data={'sort': 'reputation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_response(response)
            self.assert_items_sorted(response, 'reputation', order, enums.OrderingFieldType.INTEGER)

    def test_sort_by_creation(self):
        """Test the user list endpoint sorted by user creation date.
        """
        for order in enums.OrderingDirection:
            users = random.sample(list(models.SiteUser.objects.all()), 3)
            response = self.client.get(
                reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                data={'sort': 'creation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_name(self):
        """Test the user list endpoint sorted by username.
        """
        for order in enums.OrderingDirection:
            users = random.sample(list(models.SiteUser.objects.all()), 3)
            response = self.client.get(
                reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                data={'sort': 'name', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_response(response)
            self.assert_items_sorted(response, 'display_name', order, enums.OrderingFieldType.STRING)

    def test_sort_by_modified(self):
        """Test the user list endpoint sorted by last modified date.
        """
        for order in enums.OrderingDirection:
            users = random.sample(list(models.SiteUser.objects.all()), 3)
            response = self.client.get(
                reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                data={'sort': 'modified', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_response(response)
            self.assert_items_sorted(response, 'last_modified_date', order, enums.OrderingFieldType.DATE)

    def test_range_by_reputation(self):
        """Test the user list endpoint range by reputation.
        """
        min_value, max_value = self.generate_random_integers(max_value=500_000)
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'reputation', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)
        self.assert_items_in_range(response, 'reputation', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_creation(self):
        """Test the user list endpoint range by user creation date.
        """
        min_value, max_value = self.generate_random_date_range()
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_name(self):
        """Test the user list endpoint range by username.
        """
        min_value = 'k'
        max_value = 't'
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)
        self.assert_items_in_range(response, 'display_name', enums.OrderingFieldType.STRING, min_value, max_value)

    def test_range_by_modified(self):
        """Test the user list endpoint range by user last modified date.
        """
        min_value, max_value = self.generate_random_date_range()
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'modified', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_response(response)
        self.assert_items_in_range(response, 'last_modified_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_date_range(self):
        """Test the user list endpoint by date range.
        """
        from_date, to_date = self.generate_random_date_range()
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'fromdate': from_date.isoformat(), 'todate': to_date.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, from_date, to_date)
