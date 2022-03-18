"""Answers view set testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..test_data import setup_test_data
from stackexchange import models


class AnswerTests(APITestCase):
    """Answer view set retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        setup_test_data()

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
