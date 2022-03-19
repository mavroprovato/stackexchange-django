"""Posts view set retrieve testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import models
from stackexchange.tests import factories


class PostRetrieveTests(APITestCase):
    """Post view set retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.QuestionAnswerFactory.create_batch(size=10)

    def test(self):
        """Test the post detail endpoint.
        """
        # Test getting one post
        post = random.sample(list(models.Post.objects.all()), 1)[0]
        response = self.client.get(reverse('post-detail', kwargs={'pk': post.pk}))
        self.assertEqual(response.json()['items'][0]['post_id'], post.pk)

    def test_multiple(self):
        """Test the post detail endpoint for multiple ids.
        """
        # Test getting multiple posts
        posts = random.sample(list(models.Post.objects.all()), 3)
        response = self.client.get(reverse('post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual({row['post_id'] for row in response.json()['items']}, {post.pk for post in posts})
