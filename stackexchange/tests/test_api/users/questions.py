"""Users API testing
"""
import random

import dateutil.parser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..test_data import setup_test_data
from stackexchange import enums, models


class UserQuestionTests(APITestCase):
    """Users view set question tests
    """
    @classmethod
    def setUpTestData(cls):
        setup_test_data()

    def test(self):
        """Test user questions endpoint
        """
        # Test that the list endpoint returns successfully
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-questions', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user information returned is correct
        for row in response.json()['items']:
            question = models.Post.objects.get(pk=row['question_id'])
            self.assertEqual(row['owner']['reputation'], question.owner.reputation)
            self.assertEqual(row['owner']['user_id'], question.owner.pk)
            self.assertEqual(row['owner']['display_name'], question.owner.display_name)
            self.assertEqual(row['view_count'], question.view_count)
            self.assertEqual(row['accepted_answer_id'], getattr(question.accepted_answer, 'pk', None))
            self.assertEqual(row['answer_count'], question.answer_count)
            self.assertEqual(row['score'], question.score)
            self.assertEqual(dateutil.parser.parse(row['last_activity_date']), question.last_activity_date)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), question.creation_date)
            self.assertEqual(dateutil.parser.parse(row['last_edit_date']), question.last_edit_date)
            self.assertEqual(row['content_license'], enums.ContentLicense[question.content_license].name)
            self.assertEqual(row['title'], question.title)

    def test_sort_by_activity(self):
        """Test the user question list sorted by question activity date.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'activity', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        activity_dates = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(activity_dates, sorted(activity_dates))

        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'activity', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        activity_dates = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(activity_dates, sorted(activity_dates, reverse=True))

    def test_sort_by_creation_date(self):
        """Test the user question list sorted by user creation date.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'creation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates))

        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputation = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputation, sorted(reputation, reverse=True))

    def test_sort_by_votes(self):
        """Test the user question list sorted by votes.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'votes', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        votes = [row['score'] for row in response.json()['items']]
        self.assertListEqual(votes, sorted(votes))

        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'votes', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        votes = [row['score'] for row in response.json()['items']]
        self.assertListEqual(votes, sorted(votes, reverse=True))
