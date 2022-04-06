"""Answer comments view set testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import enums, models
from stackexchange.tests import factories
from ..comments.base import BaseCommentTestCase


class AnswerCommentsListTests(BaseCommentTestCase):
    """Answer comments view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=10)
        questions = []
        for user in users:
            questions += factories.QuestionFactory.create_batch(size=2, owner=user)
        answers = []
        for question in questions:
            answers += factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(users))
        for answer in answers:
            factories.CommentFactory.create_batch(size=2, post=answer, user=random.choice(users))

    def test(self):
        """Test the answer comments endpoint
        """
        answer = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 1)[0]
        response = self.client.get(reverse('answer-comments', kwargs={'pk': answer.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the answer comments endpoint for multiple answers
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('answer-comments', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}))
        self.assert_items_equal(response)

    def test_sort_by_creation(self):
        """Test the answer comments list sorted by comment creation date.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('answer-comments', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'creation', 'order': 'asc'}
        )
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(
            reverse('answer-comments', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'creation', 'order': 'desc'}
        )
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the answer comments list sorted by comment votes.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('answer-comments', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'votes', 'order': 'asc'}
        )
        self.assert_sorted(response, 'score')

        response = self.client.get(reverse('comment-list'), data={'sort': 'votes', 'order': 'desc'})
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_creation(self):
        """Test the answer comments list endpoint range by creation date.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('answer-comments', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'creation', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'reputation', min_value, max_value)

    def test_range_by_votes(self):
        """Test the answer comments list endpoint range by comment score.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        min_value = 10
        max_value = 1000
        response = self.client.get(
            reverse('answer-comments', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'score', min_value, max_value)

    def test_date_range(self):
        """Test the answer comments list endpoint date range.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        from_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('answer-comments', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}), data={
                'fromdate': from_value, 'todate': to_value
            }
        )
        self.assert_range(response, 'creation_date', from_value, to_value)
