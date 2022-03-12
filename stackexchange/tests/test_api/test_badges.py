"""Badges view set testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums, models
from .. import factories


class BadgeTests(APITestCase):
    """Badges view set tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.BadgeFactory.create_batch(size=100)

    def test_list(self):
        """Test badges list endpoint
        """
        response = self.client.get(reverse('badge-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the badge information returned is correct
        for row in response.json()['items']:
            badge = models.Badge.objects.get(pk=row['badge_id'])
            self.assertEqual(row['badge_type'], enums.BadgeType(badge.badge_type).name.lower())
            self.assertEqual(row['rank'], enums.BadgeClass(badge.badge_class).name.lower())
            self.assertEqual(row['name'], badge.name)

    def test_list_sort_by_rank(self):
        """Test the badges list sorted by badge rank.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'rank', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_ranks = [enums.BadgeClass[row['rank'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_ranks, sorted(badge_ranks))

        response = self.client.get(reverse('badge-list'), data={'sort': 'rank', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_ranks = [enums.BadgeClass[row['rank'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_ranks, sorted(badge_ranks, reverse=True))

    def test_list_sort_by_name(self):
        """Test the badges list sorted by badge name.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'name', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_names = [row['name'].lower() for row in response.json()['items']]
        self.assertListEqual(badge_names, sorted(badge_names))

        response = self.client.get(reverse('badge-list'), data={'sort': 'name', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_names = [row['name'].lower() for row in response.json()['items']]
        self.assertListEqual(badge_names, sorted(badge_names, reverse=True))

    def test_list_sort_by_type(self):
        """Test the badges list sorted by badge type.
        """
        response = self.client.get(reverse('badge-list'), data={'sort': 'type', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [enums.BadgeType[row['badge_type'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types))

        response = self.client.get(reverse('badge-list'), data={'sort': 'type', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [enums.BadgeType[row['badge_type'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types, reverse=True))

    def test_detail(self):
        """Test the badges detail endpoint.
        """
        badge = random.sample(list(models.Badge.objects.all()), 1)[0]
        response = self.client.get(reverse('badge-detail', kwargs={'pk': badge.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['items'][0]['badge_id'], badge.pk)

    def test_detail_multiple(self):
        """Test the badges detail endpoint for multiple ids.
        """
        badges = random.sample(list(models.Badge.objects.all()), 3)
        response = self.client.get(reverse('badge-detail', kwargs={'pk': ';'.join(str(badge.pk) for badge in badges)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual({row['badge_id'] for row in response.json()['items']}, {badge.pk for badge in badges})

    def test_named(self):
        """Test badges named endpoint
        """
        response = self.client.get(reverse('badge-named'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the badge information returned is correct
        for row in response.json()['items']:
            badge = models.Badge.objects.get(pk=row['badge_id'])
            self.assertEqual(row['badge_type'], 'named')
            self.assertEqual(row['rank'], enums.BadgeClass(badge.badge_class).name.lower())
            self.assertEqual(row['name'], badge.name)

    def test_named_sort_by_rank(self):
        """Test the badges named sorted by badge rank.
        """
        response = self.client.get(reverse('badge-named'), data={'sort': 'rank', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_ranks = [enums.BadgeClass[row['rank'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_ranks, sorted(badge_ranks))

        response = self.client.get(reverse('badge-named'), data={'sort': 'rank', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_ranks = [enums.BadgeClass[row['rank'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_ranks, sorted(badge_ranks, reverse=True))

    def test_named_sort_by_name(self):
        """Test the badges named sorted by badge name.
        """
        response = self.client.get(reverse('badge-named'), data={'sort': 'name', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_names = [row['name'].lower() for row in response.json()['items']]
        self.assertListEqual(badge_names, sorted(badge_names))

        response = self.client.get(reverse('badge-named'), data={'sort': 'name', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_names = [row['name'].lower() for row in response.json()['items']]
        self.assertListEqual(badge_names, sorted(badge_names, reverse=True))

    def test_named_sort_by_type(self):
        """Test the badges named sorted by badge type.
        """
        response = self.client.get(reverse('badge-named'), data={'sort': 'type', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [enums.BadgeType[row['badge_type'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types))

        response = self.client.get(reverse('badge-named'), data={'sort': 'type', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [enums.BadgeType[row['badge_type'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types, reverse=True))

    def test_recipients(self):
        """Test badges recipients endpoint
        """
        response = self.client.get(reverse('badge-recipients'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tags(self):
        """Test badges tags endpoint
        """
        response = self.client.get(reverse('badge-tags'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the badge information returned is correct
        for row in response.json()['items']:
            badge = models.Badge.objects.get(pk=row['badge_id'])
            self.assertEqual(row['badge_type'], 'tag_based')
            self.assertEqual(row['rank'], enums.BadgeClass(badge.badge_class).name.lower())
            self.assertEqual(row['name'], badge.name)

    def test_tags_sort_by_rank(self):
        """Test the badges tags sorted by badge rank.
        """
        response = self.client.get(reverse('badge-tags'), data={'sort': 'rank', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_ranks = [enums.BadgeClass[row['rank'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_ranks, sorted(badge_ranks))

        response = self.client.get(reverse('badge-tags'), data={'sort': 'rank', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_ranks = [enums.BadgeClass[row['rank'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_ranks, sorted(badge_ranks, reverse=True))

    def test_tags_sort_by_name(self):
        """Test the badges tags sorted by badge name.
        """
        response = self.client.get(reverse('badge-tags'), data={'sort': 'name', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_names = [row['name'].lower() for row in response.json()['items']]
        self.assertListEqual(badge_names, sorted(badge_names))

        response = self.client.get(reverse('badge-tags'), data={'sort': 'name', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_names = [row['name'].lower() for row in response.json()['items']]
        self.assertListEqual(badge_names, sorted(badge_names, reverse=True))

    def test_tags_sort_by_type(self):
        """Test the badges tags sorted by badge type.
        """
        response = self.client.get(reverse('badge-tags'), data={'sort': 'type', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [enums.BadgeType[row['badge_type'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types))

        response = self.client.get(reverse('badge-tags'), data={'sort': 'type', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badge_types = [enums.BadgeType[row['badge_type'].upper()].value for row in response.json()['items']]
        self.assertListEqual(badge_types, sorted(badge_types, reverse=True))
