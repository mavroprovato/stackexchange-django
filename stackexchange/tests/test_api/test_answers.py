"""Answers view set testing
"""
import dateutil.parser
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .. import factories
from stackexchange import enums, models


class AnswerTests(APITestCase):
    """Answer view set tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.AnswersFactory.create_batch(size=1000)

    def test_list(self):
        """Test answer list endpoint
        """
        response = self.client.get(reverse('answer-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for row in response.json()['items']:
            answer = models.Post.objects.get(pk=row['answer_id'])
            self.assertEqual(row['is_accepted'], bool(answer.accepted_answer_id))
            self.assertEqual(row['score'], answer.score)
            self.assertEqual(dateutil.parser.parse(row['last_activity_date']), answer.last_activity_date)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), answer.creation_date)
            self.assertEqual(row['content_license'], enums.ContentLicense[answer.content_license].name)

    def test_list_sort_by_activity(self):
        """Test the answer list sorted by activity date.
        """
        response = self.client.get(reverse('answer-list'), data={'sort': 'activity', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('answer-list'), data={'sort': 'activity', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_list_sort_by_creation(self):
        """Test the answer list sorted by creation date.
        """
        response = self.client.get(reverse('answer-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('answer-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_list_sort_by_votes(self):
        """Test the answer list sorted by votes.
        """
        response = self.client.get(reverse('answer-list'), data={'sort': 'votes', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['score'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('answer-list'), data={'sort': 'votes', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['score'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_detail(self):
        """Test the answer detail endpoint.
        """
        # Test getting one answer
        post = random.sample(list(models.Post.objects.all()), 1)[0]
        response = self.client.get(reverse('answer-detail', kwargs={'pk': post.pk}))
        self.assertEqual(response.json()['items'][0]['answer_id'], post.pk)

    def test_detail_multiple(self):
        """Test the answer detail endpoint for multiple ids.
        """
        # Test getting multiple answers
        posts = random.sample(list(models.Post.objects.all()), 3)
        response = self.client.get(reverse('answer-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual({row['answer_id'] for row in response.json()['items']}, {post.pk for post in posts})

