"""Badges API retrieve testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import enums, models
from stackexchange.tests import factories
from .base import BadgeWithAwardCountTestCase


class BadgeRetrieveTests(BadgeWithAwardCountTestCase):
    """Badges retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=25)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(users), badge=random.choice(badges))

    def test(self):
        """Test the badges retrieve endpoint.
        """
        badge = random.sample(list(models.Badge.objects.all()), 1)[0]
        response = self.client.get(reverse('badge-detail', kwargs={'pk': badge.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the badges retrieve endpoint for multiple ids.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        response = self.client.get(reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}))
        self.assert_items_equal(response)

    def test_sort_by_rank(self):
        """Test the badges retrieve endpoint sorted by badge rank.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'rank', 'order': 'asc'}
        )
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value)

        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'rank', 'order': 'desc'}
        )
        self.assert_sorted(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value, reverse=True)

    def test_sort_by_name(self):
        """Test the badges retrieve endpoint sorted by badge name.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'name', 'order': 'asc'}
        )
        self.assert_sorted(response, 'name', case_insensitive=True)

        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'name', 'order': 'desc'}
        )
        self.assert_sorted(response, 'name', case_insensitive=True, reverse=True)

    def test_sort_by_type(self):
        """Test the badges retrieve endpoint sorted by badge type.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'type', 'order': 'asc'}
        )
        self.assert_sorted(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value)

        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'type', 'order': 'desc'}
        )
        self.assert_sorted(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value, reverse=True)

    def test_range_by_rank(self):
        """Test the badges retrieve endpoint range by badge rank.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        min_value = enums.BadgeClass.SILVER
        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'rank', 'min': min_value.name.lower()}
        )
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          min_value=min_value.value)
        max_value = enums.BadgeClass.SILVER
        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'rank', 'max': max_value.name.lower()}
        )
        self.assert_range(response, 'rank', transform=lambda x: enums.BadgeClass[x.upper()].value,
                          max_value=max_value.value)

    def test_range_by_name(self):
        """Test the badges retrieve endpoint range by badge name.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        min_value = 'k'
        max_value = 't'
        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'name', min_value, max_value)

    def test_range_by_type(self):
        """Test the badges retrieve endpoint range by badge type.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        min_value = enums.BadgeType.TAG_BASED
        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'type', 'min': min_value.name.lower()}
        )
        self.assert_range(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value,
                          min_value=min_value.value)
        max_value = enums.BadgeType.NAMED
        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'type', 'max': max_value.name.lower()}
        )
        self.assert_range(response, 'badge_type', transform=lambda x: enums.BadgeType[x.upper()].value,
                          max_value=max_value.value)

    def test_date_range(self):
        """Test the badges retrieve endpoint date range.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        from_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}), data={
            'fromdate': from_value, 'todate': to_value
        })
        self.assert_items_equal(response)
