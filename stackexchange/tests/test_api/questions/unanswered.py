"""Questions view set unanswered testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from .base import BaseQuestionTestCase


class QuestionUnansweredTests(BaseQuestionTestCase):
    """Question view set unanswered tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        for _ in range(100):
            answer_count = random.randint(2, 5)
            question = factories.QuestionFactory.create(answer_count=answer_count)
            for _ in range(answer_count):
                factories.AnswerFactory.create(question=question, score=random.randint(0, 2))

    def test(self):
        """Test question unanswered endpoint
        """
        response = self.client.get(reverse('api-question-unanswered'))
        self.assert_items_equal(response)
        for row in response.json()['items']:
            question = models.Post.objects.get(pk=row['question_id'])
            self.assertTrue(all(answer.score == 0 for answer in question.answers.all()))

    def test_sort_by_activity(self):
        """Test the question unanswered endpoint sorted by activity date.
        """
        response = self.client.get(reverse('api-question-unanswered'), data={'sort': 'activity', 'order': 'asc'})
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(reverse('api-question-unanswered'), data={'sort': 'activity', 'order': 'desc'})
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the question unanswered endpoint sorted by creation date.
        """
        response = self.client.get(reverse('api-question-unanswered'), data={'sort': 'creation', 'order': 'asc'})
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(reverse('api-question-unanswered'), data={'sort': 'creation', 'order': 'desc'})
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the question unanswered endpoint sorted by votes.
        """
        response = self.client.get(reverse('api-question-unanswered'), data={'sort': 'votes', 'order': 'asc'})
        self.assert_sorted(response, 'score')

        response = self.client.get(reverse('api-question-unanswered'), data={'sort': 'votes', 'order': 'desc'})
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the question unanswered endpoint range by activity.
        """
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-question-unanswered'), data={
            'sort': 'activity', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the question unanswered endpoint range by user creation date.
        """
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-question-unanswered'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the question unanswered endpoint range by votes.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-question-unanswered'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'score', min_value, max_value)
