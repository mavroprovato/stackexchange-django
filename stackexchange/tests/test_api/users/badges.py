"""Users API badges testing
"""
import random
import unittest

from django.urls import reverse

from stackexchange import enums, models
from stackexchange.tests import factories
from ..badges.base import UserBadgeTestCase


class UserBadgeTests(UserBadgeTestCase):
    """Users view set badges tests
    """
    @classmethod
    def setUpTestData(cls):
        users = factories.UserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=50)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(users), badge=random.choice(badges))

    def test(self):
        """Test the user badges endpoint
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-badges', kwargs={'pk': user.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the user badges endpoint for multiple users
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}))
        self.assert_items_equal(response)

    def test_sort_by_rank(self):
        """Test the badges list endpoint sorted by badge rank.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'rank', 'order': 'asc'}
        )
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value)

        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'rank', 'order': 'desc'}
        )
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value, reverse=True)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_sort_by_name(self):
        """Test the user badges list endpoint sorted by badge name.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'name', 'order': 'asc'}
        )
        self.assert_sorted(response, 'name')

        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'name', 'order': 'desc'}
        )
        self.assert_sorted(response, 'name', reverse=True)

    def test_sort_by_type(self):
        """Test the user badges list endpoint sorted by badge type.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'type', 'order': 'asc'}
        )
        self.assert_sorted(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value)

        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'type', 'order': 'desc'}
        )
        self.assert_sorted(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value, reverse=True)

    def test_range_by_rank(self):
        """Test the user badges list endpoint range by badge rank.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = enums.BadgeClass.SILVER
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'rank', 'min': min_value.name.lower()}
        )
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          min_value=min_value.value)
        max_value = enums.BadgeClass.SILVER
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'rank', 'max': max_value.name.lower()}
        )
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          max_value=max_value.value)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_range_by_name(self):
        """Test the user badges list endpoint range by badge name.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = 'b'
        max_value = 'x'
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'name', min_value, max_value)

    def test_range_by_type(self):
        """Test the user badges list endpoint range by badge type.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = enums.BadgeType.TAG_BASED
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'type', 'min': min_value.name.lower()}
        )
        self.assert_range(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value,
                          min_value=min_value.value)
        max_value = enums.BadgeType.NAMED
        response = self.client.get(
            reverse('user-badges', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'type', 'max': max_value.name.lower()}
        )
        self.assert_range(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value,
                          max_value=max_value.value)

