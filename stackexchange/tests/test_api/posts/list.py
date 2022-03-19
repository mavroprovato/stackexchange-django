"""Posts view set list testing
"""
import dateutil.parser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums, models
from stackexchange.tests import factories


class PostListTests(APITestCase):
    """Post view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.QuestionAnswerFactory.create_batch(size=1000)

    def test(self):
        """Test post list endpoint
        """
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the post information returned is correct
        for row in response.json()['items']:
            post = models.Post.objects.get(pk=row['post_id'])
            self.assertEqual(row['score'], post.score)
            self.assertEqual(dateutil.parser.parse(row['last_activity_date']), post.last_activity_date)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), post.creation_date)
            self.assertEqual(row['post_type'], enums.PostType(post.type).name.lower())
            self.assertEqual(row['content_license'], enums.ContentLicense[post.content_license].name)

    def test_sort_by_activity(self):
        """Test the post list sorted by activity date.
        """
        response = self.client.get(reverse('post-list'), data={'sort': 'activity', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('post-list'), data={'sort': 'activity', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_sort_by_creation(self):
        """Test the post list sorted by creation date.
        """
        response = self.client.get(reverse('post-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('post-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_sort_by_votes(self):
        """Test the post list sorted by votes.
        """
        response = self.client.get(reverse('post-list'), data={'sort': 'votes', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['score'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('post-list'), data={'sort': 'votes', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['score'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))
