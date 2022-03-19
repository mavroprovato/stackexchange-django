"""Users API badges testing
"""
import random
import unittest

from django.db.models import Min
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums, models
from stackexchange.tests import factories


class UserBadgeTests(APITestCase):
    """Users view set badges tests
    """
    @classmethod
    def setUpTestData(cls):
        # Create some users
        users = factories.UserFactory.create_batch(size=10)
        # Award some badges to the users
        for user in users:
            factories.UserBadgeFactory.create_batch(size=random.randint(0, 20), user=user)

    def test(self):
        """Test user badges endpoint
        """
        # Test that the list endpoint returns successfully
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-badges', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user information returned is correct
        for row in response.json()['items']:
            badge = models.Badge.objects.get(pk=row['badge_id'])
            self.assertEqual(row['user']['reputation'], user.reputation)
            self.assertEqual(row['user']['user_id'], user.pk)
            self.assertEqual(row['user']['display_name'], user.display_name)
            self.assertEqual(row['badge_type'], enums.BadgeType(badge.badge_type).name.lower())
            self.assertEqual(row['rank'], enums.BadgeClass(badge.badge_class).name.lower())
            self.assertEqual(row['name'], badge.name)

    def test_sort_by_rank(self):
        """Test the user badges list sorted by rank.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': user.pk}), data={'sort': 'rank', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ranks = [enums.BadgeClass[row['rank'].upper()] for row in response.json()['items']]
        self.assertListEqual(ranks, sorted(ranks))

        response = self.client.get(
            reverse('user-badges', kwargs={'pk': user.pk}), data={'sort': 'rank', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ranks = [enums.BadgeClass[row['rank'].upper()] for row in response.json()['items']]
        self.assertListEqual(ranks, sorted(ranks, reverse=True))

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_sort_by_name(self):
        """Test the user badges list sorted by name.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': user.pk}), data={'sort': 'name', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [row['name'] for row in response.json()['items']]
        self.assertListEqual(names, sorted(names))

        response = self.client.get(
            reverse('user-badges', kwargs={'pk': user.pk}), data={'sort': 'name', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [row['name'] for row in response.json()['items']]
        self.assertListEqual(names, sorted(names, reverse=True))

    def test_sort_by_type(self):
        """Test the user badges list sorted by type.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': user.pk}), data={'sort': 'type', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [row['badge_type'] for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types))

        response = self.client.get(
            reverse('user-badges', kwargs={'pk': user.pk}), data={'sort': 'type', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [row['badge_type'] for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types, reverse=True))

    def test_sort_by_awarded(self):
        """Test the user badges list sorted by date awarded.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': user.pk}), data={'sort': 'awarded', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        awarded_dates = [
            models.UserBadge.objects.filter(
                badge_id=row['badge_id'], user=user
            ).aggregate(date_awarded=Min('date_awarded'))['date_awarded'] for row in response.json()['items']
        ]
        self.assertListEqual(awarded_dates, sorted(awarded_dates))

        response = self.client.get(
            reverse('user-badges', kwargs={'pk': user.pk}), data={'sort': 'awarded', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        awarded_dates = [
            models.UserBadge.objects.filter(
                badge_id=row['badge_id'], user=user
            ).aggregate(date_awarded=Min('date_awarded'))['date_awarded'] for row in response.json()['items']
        ]
        self.assertListEqual(awarded_dates, sorted(awarded_dates, reverse=True))
