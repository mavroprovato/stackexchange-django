"""Answers view set list testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange.tests import factories
from .base import BaseAnswerTestCase


class AnswerListTests(BaseAnswerTestCase):
    """Answer view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=100)
        questions = []
        for user in users:
            questions += factories.QuestionFactory.create_batch(size=2, owner=user)
        for question in questions:
            factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(users))

    def test(self):
        """Test answer list endpoint
        """
        response = self.client.get(reverse('answer-list'))
        self.assert_items_equal(response)

    def test_sort_by_activity(self):
        """Test the answer list endpoint sorted by activity date.
        """
        response = self.client.get(reverse('answer-list'), data={'sort': 'activity', 'order': 'asc'})
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(reverse('answer-list'), data={'sort': 'activity', 'order': 'desc'})
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the answer list endpoint sorted by creation date.
        """
        response = self.client.get(reverse('answer-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(reverse('answer-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the answer list endpoint sorted by votes.
        """
        response = self.client.get(reverse('answer-list'), data={'sort': 'votes', 'order': 'asc'})
        self.assert_sorted(response, 'score')

        response = self.client.get(reverse('answer-list'), data={'sort': 'votes', 'order': 'desc'})
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the answer list endpoint range by activity.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('answer-list'), data={
            'sort': 'name', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the answer list endpoint range by user creation date.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('answer-list'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the answer list endpoint range by votes.
        """
        min_value = 10
        max_value = 1000
        response = self.client.get(reverse('answer-list'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'score', min_value, max_value)

    def test_date_range(self):
        """Test the answer list endpoint date range.
        """
        from_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('answer-list'), data={
            'fromdate': from_value, 'todate': to_value
        })
        self.assert_range(response, 'creation_date', from_value, to_value)
