"""Comments view set testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import models
from stackexchange.tests import factories


class CommentRetrieveTests(APITestCase):
    """Comment view set retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.CommentFactory.create_batch(size=10)

    def test(self):
        """Test the comment retrieve endpoint.
        """
        # Test getting one comment
        comment = random.sample(list(models.Comment.objects.all()), 1)[0]
        response = self.client.get(reverse('comment-detail', kwargs={'pk': comment.pk}))
        self.assertEqual(response.json()['items'][0]['comment_id'], comment.pk)

    def test_multiple(self):
        """Test the comment retrieve endpoint for multiple ids.
        """
        # Test getting multiple comments
        comments = random.sample(list(models.Comment.objects.all()), 3)
        response = self.client.get(
            reverse('comment-detail', kwargs={'pk': ';'.join(str(comment.pk) for comment in comments)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual(
            {row['comment_id'] for row in response.json()['items']}, {comment.pk for comment in comments})
