"""Comments view list testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums
from stackexchange.tests import base, factories


class CommentListTests(base.BaseTestCase):
    """Comment view set list tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)

    def test_sort_by_creation_date(self):
        """Test the answer list endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-comment-list'), data={'sort': 'creation', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_comment_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_votes(self):
        """Test the answer list endpoint sorted by votes.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-comment-list'), data={'sort': 'votes', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_comment_response(response)
            self.assert_items_sorted(response, 'score', order, enums.OrderingFieldType.INTEGER)

    def test_range_by_creation_date(self):
        """Test the comment list endpoint range by creation date.
        """
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(reverse('api-comment-list'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_votes(self):
        """Test the comment list endpoint range by votes.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-comment-list'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)
        self.assert_items_in_range(response, 'score', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_date_range(self):
        """Test the comments list endpoint date range.
        """
        from_date, to_date = self.generate_random_date_range()
        response = self.client.get(reverse('api-comment-list'), data={
            'fromdate': from_date.isoformat(), 'todate': to_date.isoformat()
        })
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, from_date, to_date)
