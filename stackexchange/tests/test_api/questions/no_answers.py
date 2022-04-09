"""Questions view set no answers testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange.tests import factories
from .base import BaseQuestionTestCase


class QuestionNoAnswerTests(BaseQuestionTestCase):
    """Question view set no answer tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        for _ in range(100):
            factories.QuestionFactory.create(answer_count=random.randint(0, 3))

    def test(self):
        """Test question no answers endpoint
        """
        response = self.client.get(reverse('question-no-answers'))
        self.assert_items_equal(response)
        self.assertTrue(all(row['answer_count'] == 0 for row in response.json()['items']))

    def test_sort_by_activity(self):
        """Test the question no answers endpoint sorted by activity date.
        """
        response = self.client.get(reverse('question-no-answers'), data={'sort': 'activity', 'order': 'asc'})
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(reverse('question-no-answers'), data={'sort': 'activity', 'order': 'desc'})
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the question no answers endpoint sorted by creation date.
        """
        response = self.client.get(reverse('question-no-answers'), data={'sort': 'creation', 'order': 'asc'})
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(reverse('question-no-answers'), data={'sort': 'creation', 'order': 'desc'})
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the question no answers endpoint sorted by votes.
        """
        response = self.client.get(reverse('question-no-answers'), data={'sort': 'votes', 'order': 'asc'})
        self.assert_sorted(response, 'score')

        response = self.client.get(reverse('question-no-answers'), data={'sort': 'votes', 'order': 'desc'})
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the question no answers endpoint range by activity.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('question-no-answers'), data={
            'sort': 'name', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the question no answers endpoint range by user creation date.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('question-no-answers'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the question no answers endpoint range by votes.
        """
        min_value = 10
        max_value = 1000
        response = self.client.get(reverse('question-no-answers'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'score', min_value, max_value)
