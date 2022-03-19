"""Comments view set testing
"""
import dateutil.parser

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums, models
from stackexchange.tests import factories


class CommentListTests(APITestCase):
    """Comment view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.CommentFactory.create_batch(size=100)

    def test(self):
        """Test comment list endpoint
        """
        response = self.client.get(reverse('comment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user information returned is correct
        for row in response.json()['items']:
            comment = models.Comment.objects.get(pk=row['comment_id'])
            self.assertEqual(row['owner']['reputation'], comment.user.reputation)
            self.assertEqual(row['owner']['user_id'], comment.user.pk)
            self.assertEqual(row['owner']['display_name'], comment.user.display_name)
            self.assertEqual(row['score'], comment.score)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), comment.creation_date)
            self.assertEqual(row['post_id'], comment.post.pk)
            self.assertEqual(row['content_license'], enums.ContentLicense[comment.content_license].name)

    def test_sort_by_creation_date(self):
        """Test the comment list sorted by comment creation date.
        """
        response = self.client.get(reverse('comment-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates))

        response = self.client.get(reverse('comment-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputation = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputation, sorted(reputation, reverse=True))

    def test_sort_by_votes(self):
        """Test the comment list sorted by comment votes.
        """
        response = self.client.get(reverse('comment-list'), data={'sort': 'votes', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['score'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('comment-list'), data={'sort': 'votes', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['score'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))
