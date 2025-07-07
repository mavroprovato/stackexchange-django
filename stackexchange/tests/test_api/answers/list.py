"""Tests for the answers list view.
"""
import datetime
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums
from stackexchange.tests import base, factories


class AnswerListTests(base.BaseTestCase):
    """Answer view set list tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=100)
        questions = []
        for site_user in site_users:
            questions += factories.QuestionFactory.create_batch(size=2, owner=site_user)
        for question in questions:
            factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(site_users))

    def test(self):
        """Test answer list endpoint
        """
        response = self.client.get(reverse('api-answer-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)

    def test_sort_by_activity(self):
        """Test the answer list endpoint sorted by activity date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-answer-list'), data={'sort': 'activity', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'last_activity_date', order)

    def test_sort_by_creation_date(self):
        """Test the answer list endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-answer-list'), data={'sort': 'creation', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'creation_date', order)

    def test_sort_by_votes(self):
        """Test the answer list endpoint sorted by votes.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-answer-list'), data={'sort': 'votes', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'score', order)

    def test_range_by_activity(self):
        """Test the answer list endpoint range by activity date.
        """
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-answer-list'), data={
            'sort': 'activity', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'last_activity_date', min_value.isoformat(), max_value.isoformat())

    def test_range_by_creation_date(self):
        """Test the answer list endpoint range by creation date.
        """
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-answer-list'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'creation_date', min_value.isoformat(), max_value.isoformat())

    def test_range_by_votes(self):
        """Test the answer list endpoint range by votes.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-answer-list'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'score', min_value, max_value)

    def test_date_range(self):
        """Test the answer list endpoint date range.
        """
        from_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-answer-list'), data={
            'fromdate': from_value.isoformat(), 'todate': from_value.isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'creation_date', from_value.isoformat(), to_value.isoformat())
