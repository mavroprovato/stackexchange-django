"""Badges API named testing
"""
import random
import typing

from django.urls import reverse

from stackexchange import enums, models
from stackexchange.tests import factories
from .base import BadgeWithAwardCountTestCase


class BadgeNamedTests(BadgeWithAwardCountTestCase):
    """Badges named tests
    """
    @classmethod
    def setUpTestData(cls):
        users = factories.UserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=25)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(users), badge=random.choice(badges))

    def assert_items_equal(self, response, model_class: typing.ClassVar = models.Badge,
                           obj_filter: typing.Union[str, dict] = 'badge_id', multiple: bool = False,
                           attributes: dict = None):
        """Overridden in order to validate that we only get named badges
        """
        super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)
        self.assertTrue(
            all(row['badge_type'] == enums.BadgeType.NAMED.name.lower() for row in response.json()['items']))

    def test(self):
        """Test badges named endpoint
        """
        response = self.client.get(reverse('badge-named'))
        self.assert_items_equal(response)

    def test_sort_by_rank(self):
        """Test the badges named endpoint sorted by badge rank.
        """
        response = self.client.get(reverse('badge-named'), data={'sort': 'rank', 'order': 'asc'})
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value)

        response = self.client.get(reverse('badge-named'), data={'sort': 'rank', 'order': 'desc'})
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value, reverse=True)

    def test_sort_by_name(self):
        """Test the badges named endpoint sorted by badge name.
        """
        response = self.client.get(reverse('badge-named'), data={'sort': 'name', 'order': 'asc'})
        self.assert_sorted(response, 'name', case_insensitive=True)

        response = self.client.get(reverse('badge-named'), data={'sort': 'name', 'order': 'desc'})
        self.assert_sorted(response, 'name', case_insensitive=True, reverse=True)

    def test_range_by_rank(self):
        """Test the badges named endpoint range by badge rank.
        """
        min_value = enums.BadgeClass.SILVER
        response = self.client.get(reverse('badge-named'), data={
            'sort': 'rank', 'min': min_value.name.lower()
        })
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          min_value=min_value.value)
        max_value = enums.BadgeClass.SILVER
        response = self.client.get(reverse('badge-named'), data={
            'sort': 'rank', 'max': max_value.name.lower()
        })
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          max_value=max_value.value)

    def test_range_by_name(self):
        """Test the badges named endpoint range by badge name.
        """
        min_value = 'k'
        max_value = 't'
        response = self.client.get(reverse('badge-named'), data={'sort': 'name', 'min': min_value, 'max': max_value})
        self.assert_range(response, 'name', min_value, max_value)
