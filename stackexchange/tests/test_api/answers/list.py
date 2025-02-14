"""Answers view set list testing
"""
import datetime
import random

from django.urls import reverse
from rest_framework import status

from stackexchange.tests import factories
from .base import BaseAnswerTestCase


class AnswerListTests(BaseAnswerTestCase):
    """Answer view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        site = factories.SiteFactory.create()
        site_users = factories.SiteUserFactory.create_batch(site=site, size=100)
        questions = []
        for site_user in site_users:
            questions += factories.QuestionFactory.create_batch(size=2, owner=site_user)
        for question in questions:
            factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(site_users))

    def test(self):
        """Test answer list endpoint
        """
        response = self.client.get(reverse('api-answer-list'))
        self.assert_items_equal(response)

    def test_sort_by_activity(self):
        """Test the answer list endpoint sorted by activity date.
        """
        response = self.client.get(reverse('api-answer-list'), data={'sort': 'activity', 'order': 'asc'})
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(reverse('api-answer-list'), data={'sort': 'activity', 'order': 'desc'})
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the answer list endpoint sorted by creation date.
        """
        response = self.client.get(reverse('api-answer-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(reverse('api-answer-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the answer list endpoint sorted by votes.
        """
        response = self.client.get(reverse('api-answer-list'), data={'sort': 'votes', 'order': 'asc'})
        self.assert_sorted(response, 'score')

        response = self.client.get(reverse('api-answer-list'), data={'sort': 'votes', 'order': 'desc'})
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the answer list endpoint range by activity.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-answer-list'), data={
            'sort': 'activity', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the answer list endpoint range by user creation date.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-answer-list'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the answer list endpoint range by votes.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-answer-list'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'score', min_value, max_value)

    def test_date_range(self):
        """Test the answer list endpoint date range.
        """
        from_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-answer-list'), data={
            'fromdate': from_value, 'todate': to_value
        })
        self.assert_range(response, 'creation_date', from_value, to_value)

    def test_invalid_date_range(self):
        """Test the answer list endpoint with invalid date range
        """
        response = self.client.get(reverse('api-answer-list'), data={'fromdate': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(reverse('api-answer-list'), data={'todate': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
