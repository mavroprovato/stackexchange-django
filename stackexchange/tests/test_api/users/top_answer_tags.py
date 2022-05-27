"""Users API top answer tags testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import models
from stackexchange.tests import factories
from .base import BaseTestCase


class UserTopAnswerTagTests(BaseTestCase):
    """Users view set answer tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=100)
        tags = factories.TagFactory.create_batch(size=10)
        questions = []
        for user in users:
            questions += factories.QuestionFactory.create_batch(size=3, owner=user)
        for question in questions:
            for tag in random.sample(tags, 3):
                factories.PostTagFactory.create(post=question, tag=tag)

    def test(self):
        """Test user answer tags endpoint.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('api-user-top-answer-tags', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        question_scores = [row['answer_score'] for row in response.json()['items']]
        self.assertEqual(question_scores, sorted(question_scores, reverse=True))

    def test_multiple(self):
        """Test the user answer tags endpoint for multiple ids.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-top-answer-tags', kwargs={'pk': ';'.join(str(user.pk) for user in users)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        question_scores = [row['answer_score'] for row in response.json()['items']]
        self.assertEqual(question_scores, sorted(question_scores, reverse=True))
