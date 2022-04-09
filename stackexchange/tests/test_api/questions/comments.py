"""Question view set comments testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import enums, models
from stackexchange.tests import factories
from ..comments.base import BaseCommentTestCase


class QuestionCommentsTests(BaseCommentTestCase):
    """Question view set comments tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=100)
        questions = []
        for user in users:
            questions += factories.QuestionFactory.create_batch(size=3, owner=user)
        for _ in range(1000):
            factories.CommentFactory.create(post=random.choice(questions), user=random.choice(users))

    def test(self):
        """Test comment list endpoint
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        response = self.client.get(
            reverse('question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}))
        self.assert_items_equal(response)

    def test_sort_by_creation(self):
        """Test the question comments sorted by comment creation date.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        response = self.client.get(
            reverse('question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'creation', 'order': 'asc'}
        )
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(
            reverse('question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'creation', 'order': 'desc'}
        )
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the comment list sorted by comment votes.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        response = self.client.get(
            reverse('question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'votes', 'order': 'asc'}
        )
        self.assert_sorted(response, 'score')

        response = self.client.get(
            reverse('question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'votes', 'order': 'desc'}
        )
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_creation(self):
        """Test the comments list endpoint range by creation date.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}), data={
                'sort': 'creation', 'min': min_value, 'max': max_value
            }
        )
        self.assert_range(response, 'reputation', min_value, max_value)

    def test_range_by_votes(self):
        """Test the user list endpoint range by comment score.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        min_value = 3000
        max_value = 6000
        response = self.client.get(
            reverse('question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}), data={
                'sort': 'votes', 'min': min_value, 'max': max_value
            }
        )
        self.assert_range(response, 'score', min_value, max_value)
