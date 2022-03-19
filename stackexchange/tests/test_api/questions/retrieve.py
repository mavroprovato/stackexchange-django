"""Questions view set retrieve testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import models
from stackexchange.tests import factories


class QuestionRetrieveTests(APITestCase):
    """Question view set retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.QuestionFactory.create_batch(size=1000)

    def test(self):
        """Test the question detail endpoint.
        """
        # Test getting one question
        question = random.sample(list(models.Post.objects.all()), 1)[0]
        response = self.client.get(reverse('question-detail', kwargs={'pk': question.pk}))
        self.assertEqual(response.json()['items'][0]['question_id'], question.pk)

    def test_multiple(self):
        """Test the question detail endpoint for multiple ids.
        """
        # Test getting multiple questions
        questions = random.sample(list(models.Post.objects.all()), 3)
        response = self.client.get(reverse('question-detail', kwargs={
            'pk': ';'.join(str(question.pk) for question in questions)
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual({row['question_id'] for row in response.json()['items']},
                            {question.pk for question in questions})
