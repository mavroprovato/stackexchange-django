"""Users API badges testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class UserBadgeTests(base.BaseTestCase):
    """Users view set badges tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=25)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(site_users), badge=random.choice(badges))

    def test(self):
        """Test the user badges endpoint
        """
        user = random.sample(list(models.SiteUser.objects.all()), 1)[0]
        response = self.client.get(reverse('api-user-badges', kwargs={'pk': user.unique_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_badge_response(response)

    def test_multiple(self):
        """Test the user badges endpoint for multiple users
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_badge_response(response)

    def test_sort_by_rank(self):
        """Test the user badges endpoint sorted by badge rank.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
                data={'sort': 'rank', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_badge_response(response)
            self.assert_items_sorted(response, 'rank', order, field_type=enums.OrderingFieldType.RANK)

    def test_sort_by_name(self):
        """Test the user badges endpoint sorted by badge name.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
                data={'sort': 'name', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_badge_response(response)
            self.assert_items_sorted(response, 'name', order, enums.OrderingFieldType.STRING)

    def test_sort_by_type(self):
        """Test the user badges endpoint sorted by badge type.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
                data={'sort': 'type', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_badge_response(response)
            self.assert_items_sorted(response, 'badge_type', order, field_type=enums.OrderingFieldType.BADGE_TYPE)

    def test_sort_by_awarded(self):
        """Test the user badges endpoint sorted by date awarded.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
                data={'sort': 'awarded', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_user_badge_response(response)
            self.assert_items_sorted(response, 'date_awarded', order, field_type=enums.OrderingFieldType.DATE)

    def test_range_by_rank(self):
        """Test the user badges endpoint range by badge rank.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value = enums.BadgeRank.SILVER
        response = self.client.get(
            reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
            data={'sort': 'rank', 'min': min_value.value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_badge_response(response)
        self.assert_items_in_range(response, 'rank', min_value=min_value, field_type=enums.OrderingFieldType.RANK)

        max_value = enums.BadgeRank.SILVER
        response = self.client.get(
            reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
            data={'sort': 'rank', 'max': max_value.value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_badge_response(response)
        self.assert_items_in_range(response, 'rank', max_value=max_value, field_type=enums.OrderingFieldType.RANK)

    def test_range_by_name(self):
        """Test the user badges endpoint range by badge name.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value = 'k'
        max_value = 't'
        response = self.client.get(
            reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
            data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_badge_response(response)
        self.assert_items_in_range(response, 'name', enums.OrderingFieldType.STRING, min_value, max_value)

    def test_range_by_type(self):
        """Test the user badges endpoint range by badge type.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value = enums.BadgeType.TAG_BASED
        response = self.client.get(
            reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
            data={'sort': 'type', 'min': min_value.value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_badge_response(response)
        self.assert_items_in_range(
            response, 'badge_type', min_value=min_value, field_type=enums.OrderingFieldType.BADGE_TYPE
        )
        max_value = enums.BadgeType.NAMED
        response = self.client.get(
            reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
            data={'sort': 'type', 'max': max_value.value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_badge_response(response)
        self.assert_items_in_range(
            response, 'badge_type', max_value=max_value, field_type=enums.OrderingFieldType.BADGE_TYPE
        )

    def test_range_by_awarded(self):
        """Test the user badges endpoint range by date awarded.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
            data={'sort': 'awarded', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_badge_response(response)
        self.assert_items_in_range(response, 'date_awarded', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_date_range(self):
        """Test the user list endpoint by date range.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        from_date, to_date = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-user-badges', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
            data={'fromdate': from_date.isoformat(), 'todate': to_date.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_user_badge_response(response)
        self.assert_items_in_range(response, 'date_awarded', enums.OrderingFieldType.DATE, from_date, to_date)
