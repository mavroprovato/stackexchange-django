"""Answers view set testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums, models
from stackexchange.tests import factories


class AnswerRetrieveTests(APITestCase):
    """Answer view set retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.AnswersFactory.create_batch(size=100)

    def test_detail(self):
        """Test the answer detail endpoint.
        """
        # Test getting one answer
        answer = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER.value)), 1)[0]
        response = self.client.get(reverse('answer-detail', kwargs={'pk': answer.pk}))
        self.assertEqual(response.json()['items'][0]['answer_id'], answer.pk)

    def test_detail_multiple(self):
        """Test the answer detail endpoint for multiple ids.
        """
        # Test getting multiple answers
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER.value)), 3)
        response = self.client.get(
            reverse('answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual({row['answer_id'] for row in response.json()['items']}, {answer.pk for answer in answers})
