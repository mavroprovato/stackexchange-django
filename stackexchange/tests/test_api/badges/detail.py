"""Badges API retrieve testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class BadgeRetrieveTests(base.BaseTestCase):
    """Badges retrieve tests
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
        """Test the badges retrieve endpoint.
        """
        badge = random.sample(list(models.Badge.objects.all()), 1)[0]
        response = self.client.get(reverse('api-badge-detail', kwargs={'pk': badge.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_badge_with_award_count_response(response)

    def test_multiple(self):
        """Test the badges retrieve endpoint for multiple ids.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        response = self.client.get(
            reverse('api-badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_badge_with_award_count_response(response)

    def test_sort_by_rank(self):
        """Test the badges retrieve endpoint sorted by badge rank.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
                data={'sort': 'rank', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_badge_with_award_count_response(response)
            self.assert_items_sorted(response, 'rank', order, field_type=enums.OrderingFieldType.RANK)

    def test_sort_by_name(self):
        """Test the badges retrieve endpoint sorted by badge name.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
                data={'sort': 'name', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_badge_with_award_count_response(response)
            self.assert_items_sorted(response, 'name', order, field_type=enums.OrderingFieldType.STRING)

    def test_sort_by_type(self):
        """Test the badges retrieve endpoint sorted by badge type.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
                data={'sort': 'type', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_badge_with_award_count_response(response)
            self.assert_items_sorted(response, 'badge_type', order, field_type=enums.OrderingFieldType.BADGE_TYPE)

    def test_range_by_rank(self):
        """Test the badges retrieve endpoint range by badge rank.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        min_value = enums.BadgeRank.SILVER
        response = self.client.get(
            reverse('api-badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'rank', 'min': min_value.value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_items_in_range(response, 'rank', min_value=min_value, field_type=enums.OrderingFieldType.RANK)

        max_value = enums.BadgeRank.SILVER
        response = self.client.get(
            reverse('api-badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'rank', 'max': max_value.value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_items_in_range(response, 'rank', max_value=max_value, field_type=enums.OrderingFieldType.RANK)

    def test_range_by_name(self):
        """Test the badges retrieve endpoint range by badge name.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        min_value = 'k'
        max_value = 't'
        response = self.client.get(
            reverse('api-badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_items_in_range(response, 'rank', max_value=max_value, field_type=enums.OrderingFieldType.BADGE_TYPE)

    def test_range_by_type(self):
        """Test the badges retrieve endpoint range by badge type.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        min_value = enums.BadgeType.TAG_BASED
        response = self.client.get(
            reverse('api-badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'type', 'min': min_value.value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_items_in_range(
            response, 'badge_type', min_value=min_value, field_type=enums.OrderingFieldType.BADGE_TYPE
        )

        max_value = enums.BadgeType.NAMED
        response = self.client.get(
            reverse('api-badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}),
            data={'sort': 'type', 'max': max_value.value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_items_in_range(
            response, 'badge_type', max_value=max_value, field_type=enums.OrderingFieldType.BADGE_TYPE
        )
