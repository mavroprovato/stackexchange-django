"""Comments view set testing
"""
import datetime
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import models
from stackexchange.tests import factories
from .base import BaseCommentTestCase


class CommentRetrieveTests(BaseCommentTestCase):
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
        response = self.client.get(reverse('api-comment-detail', kwargs={'pk': comment.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the comment retrieve endpoint for multiple ids.
        """
        # Test getting multiple comments
        comments = random.sample(list(models.Comment.objects.all()), 3)
        response = self.client.get(
            reverse('api-comment-detail', kwargs={'pk': ';'.join(str(comment.pk) for comment in comments)}))
        self.assert_items_equal(response)

    def test_date_range(self):
        """Test the comment retrieve endpoint date range.
        """
        comments = random.sample(list(models.Comment.objects.all()), 3)
        from_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-badge-recipients-detail', kwargs={'pk': ';'.join(str(comment.pk) for comment in comments)}),
            data={'fromdate': from_value, 'todate': to_value}
        )
        self.assert_range(response, 'creation_date', from_value, to_value)
