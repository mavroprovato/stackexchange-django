"""Users API answers testing
"""
import random

import dateutil.parser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums, models
from stackexchange.tests import factories


class UserAnswerTests(APITestCase):
    """Users view set answer tests
    """
    @classmethod
    def setUpTestData(cls):
        # Create some users
        users = factories.UserFactory.create_batch(size=10)
        # Create some questions from the users
        questions = []
        for user in users:
            questions += factories.QuestionFactory.create_batch(size=random.randint(0, 3), owner=user)
        # Post some answers to the questions
        for question in questions:
            user = random.choice(users)
            factories.AnswersFactory.create_batch(size=random.randint(0, 3), question=question, owner=user)

    def test(self):
        """Test user answers endpoint
        """
        # Test that the list endpoint returns successfully
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-answers', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user information returned is correct
        for row in response.json()['items']:
            answer = models.Post.objects.get(pk=row['answer_id'])
            self.assertEqual(row['owner']['reputation'], answer.owner.reputation)
            self.assertEqual(row['owner']['user_id'], answer.owner.pk)
            self.assertEqual(row['owner']['display_name'], answer.owner.display_name)
            self.assertEqual(row['score'], answer.score)
            self.assertEqual(dateutil.parser.parse(row['last_activity_date']), answer.last_activity_date)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), answer.creation_date)
            self.assertEqual(row['question_id'], answer.question.pk)
            self.assertEqual(row['content_license'], enums.ContentLicense[answer.content_license].name)

    def test_sort_by_activity(self):
        """Test the user answer list sorted by question activity date.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'activity', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        activity_dates = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(activity_dates, sorted(activity_dates))

        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'activity', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        activity_dates = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(activity_dates, sorted(activity_dates, reverse=True))

    def test_sort_by_creation_date(self):
        """Test the user answer list sorted by user creation date.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'creation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates))

        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputation = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputation, sorted(reputation, reverse=True))

    def test_sort_by_votes(self):
        """Test the user answer list sorted by votes.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'votes', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        votes = [row['score'] for row in response.json()['items']]
        self.assertListEqual(votes, sorted(votes))

        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'votes', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        votes = [row['score'] for row in response.json()['items']]
        self.assertListEqual(votes, sorted(votes, reverse=True))
