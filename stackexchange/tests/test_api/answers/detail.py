"""Tests for the answers detail view.
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories
from .base import BaseAnswerTests


class AnswerDetailTests(BaseAnswerTests):
    """Answer view set detail tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        BaseAnswerTests.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=10)
        questions = []
        for site_user in site_users:
            questions += factories.QuestionFactory.create_batch(size=2, owner=site_user)
        for question in questions:
            factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(site_users))

    def test(self):
        """Test the question detail endpoint
        """
        answer = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 1)[0]
        response = self.client.get(reverse('api-answer-detail', kwargs={'pk': answer.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for item in response.json()['items']:
            self.assert_response_schema(item)

    def test_multiple(self):
        """Test the question detail endpoint for multiple ids.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for item in response.json()['items']:
            self.assert_response_schema(item)
