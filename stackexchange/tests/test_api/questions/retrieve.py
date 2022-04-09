"""Questions view set retrieve testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import enums, models
from stackexchange.tests import factories
from .base import BaseQuestionTestCase


class QuestionRetrieveTests(BaseQuestionTestCase):
    """Question view set retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=10)
        for user in users:
            factories.QuestionFactory.create_batch(size=2, owner=user)

    def test(self):
        """Test the question detail endpoint
        """
        question = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 1)[0]
        response = self.client.get(reverse('question-detail', kwargs={'pk': question.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the question detail endpoint for multiple ids.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        response = self.client.get(
            reverse('question-detail', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}))
        self.assert_items_equal(response)

    def test_sort_by_activity(self):
        """Test the question detail endpoint sorted by activity date.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        response = self.client.get(
            reverse('question-detail', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'activity', 'order': 'asc'}
        )
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(
            reverse('question-detail', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'activity', 'order': 'desc'}
        )
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the question detail endpoint sorted by creation date.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        response = self.client.get(
            reverse('question-detail', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'creation', 'order': 'asc'}
        )
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(
            reverse('question-detail', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'creation', 'order': 'desc'}
        )
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the question detail endpoint sorted by votes.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        response = self.client.get(
            reverse('question-detail', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'votes', 'order': 'asc'}
        )
        self.assert_sorted(response, 'score')

        response = self.client.get(
            reverse('question-detail', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'votes', 'order': 'desc'}
        )
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the question detail endpoint range by activity.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('question-detail', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the question detail endpoint range by user creation date.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('question-detail', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the question detail endpoint range by votes.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        min_value = 3000
        max_value = 6000
        response = self.client.get(
            reverse('question-detail', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'score', min_value, max_value)
