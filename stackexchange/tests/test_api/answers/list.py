"""Tests for the answers list view.
"""
import datetime
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums
from stackexchange.tests import factories
from .base import BaseAnswerTests


class AnswerListTests(BaseAnswerTests):
    """Answer view set list tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        BaseAnswerTests.setUpClass()
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
        for item in response.json()['items']:
            self.assert_response_schema(item)

    def test_sort_by_activity(self):
        """Test the answer list endpoint sorted by activity date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-answer-list'), data={'sort': 'activity', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            for item in response.json()['items']:
                self.assert_response_schema(item)
            values = [item['last_activity_date'] for item in response.json()['items']]
            self.assertListEqual(values, sorted(values, reverse=order == enums.OrderingDirection.DESC))

    def test_sort_by_creation_date(self):
        """Test the answer list endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-answer-list'), data={'sort': 'creation', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            for item in response.json()['items']:
                self.assert_response_schema(item)
            values = [item['creation_date'] for item in response.json()['items']]
            self.assertListEqual(values, sorted(values, reverse=order == enums.OrderingDirection.DESC))

    def test_sort_by_votes(self):
        """Test the answer list endpoint sorted by votes.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-answer-list'), data={'sort': 'votes', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            for item in response.json()['items']:
                self.assert_response_schema(item)
            values = [item['score'] for item in response.json()['items']]
            self.assertListEqual(values, sorted(values, reverse=order == enums.OrderingDirection.DESC))

    def test_range_by_activity(self):
        """Test the answer list endpoint range by activity date.
        """
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-answer-list'), data={
            'sort': 'activity', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.json()['items']:
            self.assertTrue(min_value.isoformat() <= item['last_activity_date'] <= max_value.isoformat())

    def test_range_by_creation_date(self):
        """Test the answer list endpoint range by creation date.
        """
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-answer-list'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.json()['items']:
            self.assertTrue(min_value.isoformat() <= item['creation_date'] <= max_value.isoformat())

    def test_range_by_votes(self):
        """Test the answer list endpoint range by votes.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-answer-list'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.json()['items']:
            self.assertTrue(min_value <= item['score'] <= max_value)
