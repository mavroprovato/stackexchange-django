"""Questions view set list testing
"""
import datetime

from django.urls import reverse

from stackexchange.tests import factories
from .base import BaseQuestionTestCase


class QuestionListTests(BaseQuestionTestCase):
    """Question view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=100)
        for user in users:
            factories.QuestionFactory.create_batch(size=3, owner=user)

    def test(self):
        """Test question list endpoint
        """
        response = self.client.get(reverse('api-question-list'))
        self.assert_items_equal(response)

    def test_sort_by_activity(self):
        """Test the question list endpoint sorted by activity date.
        """
        response = self.client.get(reverse('api-question-list'), data={'sort': 'activity', 'order': 'asc'})
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(reverse('api-question-list'), data={'sort': 'activity', 'order': 'desc'})
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the question list endpoint sorted by creation date.
        """
        response = self.client.get(reverse('api-question-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(reverse('api-question-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the question list endpoint sorted by votes.
        """
        response = self.client.get(reverse('api-question-list'), data={'sort': 'votes', 'order': 'asc'})
        self.assert_sorted(response, 'score')

        response = self.client.get(reverse('api-question-list'), data={'sort': 'votes', 'order': 'desc'})
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the question list endpoint range by activity.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-question-list'), data={
            'sort': 'name', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the question list endpoint range by user creation date.
        """
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-question-list'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the question list endpoint range by votes.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-question-list'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'score', min_value, max_value)
