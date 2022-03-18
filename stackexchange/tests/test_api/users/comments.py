"""Users API comments testing
"""
import random

import dateutil.parser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..test_data import setup_test_data
from stackexchange import enums, models


class UserCommentTests(APITestCase):
    """Users view set comments tests
    """
    @classmethod
    def setUpTestData(cls):
        setup_test_data()

    def test(self):
        """Test user comments endpoint
        """
        # Test that the list endpoint returns successfully
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-comments', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user information returned is correct
        for row in response.json()['items']:
            comment = models.Comment.objects.get(pk=row['comment_id'])
            self.assertEqual(row['owner']['reputation'], comment.user.reputation)
            self.assertEqual(row['owner']['user_id'], comment.user.pk)
            self.assertEqual(row['owner']['display_name'], comment.user.display_name)
            self.assertEqual(row['score'], comment.score)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), comment.creation_date)
            self.assertEqual(row['content_license'], enums.ContentLicense[comment.content_license].name)

    def test_sort_by_creation(self):
        """Test the user comments list sorted by creation date.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-comments', kwargs={'pk': user.pk}), data={'creation': 'rank', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates))

        response = self.client.get(
            reverse('user-comments', kwargs={'pk': user.pk}), data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates, reverse=True))

    def test_sort_by_votes(self):
        """Test the user comments list sorted by name.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-comments', kwargs={'pk': user.pk}), data={'sort': 'votes', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        scores = [row['score'] for row in response.json()['items']]
        self.assertListEqual(scores, sorted(scores))

        response = self.client.get(
            reverse('user-comments', kwargs={'pk': user.pk}), data={'sort': 'votes', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        scores = [row['score'] for row in response.json()['items']]
        self.assertListEqual(scores, sorted(scores, reverse=True))