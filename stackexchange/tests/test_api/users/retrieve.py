"""Users API retrieve testing
"""
import datetime
import random
import unittest

import dateutil.parser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import models
from stackexchange.tests import factories


class UserRetrieveTests(APITestCase):
    """User view set retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.UserFactory.create_batch(size=10)

    def test_detail(self):
        """Test the user detail endpoint.
        """
        # Test getting one user
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-detail', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['items'][0]['user_id'], user.pk)
        self.assertEqual(response.json()['items'][0]['is_employee'], user.is_employee)
        self.assertEqual(response.json()['items'][0]['reputation'], user.reputation)
        self.assertEqual(dateutil.parser.parse(response.json()['items'][0]['creation_date']), user.creation_date)
        self.assertEqual(
            dateutil.parser.parse(response.json()['items'][0]['last_modified_date']), user.last_modified_date)
        self.assertEqual(response.json()['items'][0]['location'], user.location)
        self.assertEqual(response.json()['items'][0]['website_url'], user.website_url)
        self.assertEqual(response.json()['items'][0]['display_name'], user.display_name)

    def test_detail_multiple(self):
        """Test the user detail endpoint for multiple ids.
        """
        # Test getting multiple users
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the user information returned is correct
        for row in response.json()['items']:
            user = models.User.objects.get(pk=row['user_id'])
            self.assertEqual(row['is_employee'], user.is_employee)
            self.assertEqual(row['reputation'], user.reputation)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), user.creation_date)
            self.assertEqual(dateutil.parser.parse(row['last_modified_date']), user.last_modified_date)
            self.assertEqual(row['location'], user.location)
            self.assertEqual(row['website_url'], user.website_url)
            self.assertEqual(row['display_name'], user.display_name)

    def test_sort_by_reputation(self):
        """Test the user detail endpoint sorted by user reputation.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'reputation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['reputation'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'reputation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['reputation'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_sort_by_creation_date(self):
        """Test the user detail sorted by user creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'creation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates))

        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates, reverse=True))

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_sort_by_display_name(self):
        """Test the user detail sorted by user display name.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'name', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        display_names = [row['display_name'] for row in response.json()['items']]
        self.assertListEqual(display_names, sorted(display_names))

        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'name', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        display_names = [row['display_name'] for row in response.json()['items']]
        self.assertListEqual(display_names, sorted(display_names, reverse=True))

    def test_sort_by_modified_date(self):
        """Test the user detail sorted by user modification date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'modified', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        modification_dates = [row['last_modified_date'] for row in response.json()['items']]
        self.assertListEqual(modification_dates, sorted(modification_dates))

        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'modified', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        modification_dates = [row['last_modified_date'] for row in response.json()['items']]
        self.assertListEqual(modification_dates, sorted(modification_dates, reverse=True))

    def test_range_by_reputation(self):
        """Test the user detail range by reputation.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = 10
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'reputation', 'min': min_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['reputation'] >= min_value for row in response.json()['items']))

        max_value = 1000
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'reputation', 'max': max_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['reputation'] <= max_value for row in response.json()['items']))

    def test_range_by_creation_date(self):
        """Test the user detail range by user creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'creation', 'min': min_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['creation_date'] >= min_value.isoformat() for row in response.json()['items']))

        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'creation', 'max': max_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['creation_date'] <= max_value.isoformat() for row in response.json()['items']))

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_range_by_display_name(self):
        """Test the user detail sorted by user display name.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = 'b'
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'name', 'min': min_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['display_name'] >= min_value for row in response.json()['items']))

        max_value = 'x'
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'name', 'min': min_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['display_name'] <= max_value for row in response.json()['items']))

    def test_range_by_modification_date(self):
        """Test the user detail range by user modification date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'modified', 'min': min_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['last_modified_date'] >= min_value.isoformat() for row in response.json()['items']))

        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
                                   data={'sort': 'modified', 'max': max_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(row['last_modified_date'] <= max_value.isoformat() for row in response.json()['items']))
