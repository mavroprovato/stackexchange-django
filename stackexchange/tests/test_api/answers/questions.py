"""Answer questions view set testing
"""
import datetime
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import factories
from ..questions.base import BaseQuestionTestCase


class AnswerQuestionListTests(BaseQuestionTestCase):
    """Answer questions view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        tags = factories.TagFactory.create_batch(size=100)
        users = factories.UserFactory.create_batch(size=100)
        for user in users:
            questions = factories.QuestionFactory.create_batch(size=2, owner=user)
            for question in questions:
                factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(users))
                for tag in random.sample(tags, 3):
                    factories.QuestionTagFactory.create(post=question, tag=tag)

    def test(self):
        """Test the answer questions endpoint
        """
        answer = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 1)[0]
        response = self.client.get(reverse('api-answer-questions', kwargs={'pk': answer.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the answer questions endpoint for multiple answers
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}))
        self.assert_items_equal(response)

    def test_sort_by_activity(self):
        """Test the answer questions endpoint sorted by activity date.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'activity', 'order': 'asc'}
        )
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'activity', 'order': 'desc'}
        )
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the answer questions list sorted by comment votes.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'votes', 'order': 'asc'}
        )
        self.assert_sorted(response, 'score')

        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'votes', 'order': 'desc'}
        )
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the answer questions endpoint range by activity.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_sort_by_creation(self):
        """Test the answer questions list sorted by comment creation date.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'creation', 'order': 'asc'}
        )
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'creation', 'order': 'desc'}
        )
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_range_by_votes(self):
        """Test the answer questions list endpoint range by comment score.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        min_value = 3000
        max_value = 6000
        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'score', min_value, max_value)

    def test_range_by_creation(self):
        """Test the answer questions list endpoint range by creation date.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'creation', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'reputation', min_value, max_value)

    def test_date_range(self):
        """Test the answer questions list endpoint date range.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        from_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}), data={
                'fromdate': from_value, 'todate': to_value
            }
        )
        self.assert_range(response, 'creation_date', from_value, to_value)

    def test_invalid_date_range(self):
        """Test the answer questions list endpoint with invalid date range
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}), data={
                'fromdate': 'invalid',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(
            reverse('api-answer-questions', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}), data={
                'todate': 'invalid',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
