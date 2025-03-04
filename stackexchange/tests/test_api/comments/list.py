"""Comments view set testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange.tests import factories
from .base import BaseCommentTestCase


class CommentListTests(BaseCommentTestCase):
    """Comment view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        site_users = factories.SiteUserFactory.create_batch(size=100)
        posts = []
        for site_user in site_users:
            for _ in range(3):
                posts.append(factories.QuestionAnswerFactory.create(owner=site_user))
        for _ in range(1000):
            for _ in range(3):
                factories.PostCommentFactory.create(post=random.choice(posts), user=random.choice(site_users))

    def test(self):
        """Test comment list endpoint
        """
        response = self.client.get(reverse('api-comment-list'))
        self.assert_items_equal(response)

    def test_sort_by_creation(self):
        """Test the comment list sorted by comment creation date.
        """
        response = self.client.get(reverse('api-comment-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(reverse('api-comment-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the comment list sorted by comment votes.
        """
        response = self.client.get(reverse('api-comment-list'), data={'sort': 'votes', 'order': 'asc'})
        self.assert_sorted(response, 'score')

        response = self.client.get(reverse('api-comment-list'), data={'sort': 'votes', 'order': 'desc'})
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_creation(self):
        """Test the comments list endpoint range by creation date.
        """
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-comment-list'), data={
            'sort': 'creation', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'reputation', min_value, max_value)

    def test_range_by_votes(self):
        """Test the comments list endpoint range by comment score.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-comment-list'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'score', min_value, max_value)

    def test_date_range(self):
        """Test the comments list endpoint date range.
        """
        from_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-comment-list'), data={
            'fromdate': from_value, 'todate': to_value
        })
        self.assert_range(response, 'creation_date', from_value, to_value)
