"""Users API answers testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from ..answers.base import BaseAnswerTestCase


class UserAnswerTests(BaseAnswerTestCase):
    """Users view set answer tests
    """
    @classmethod
    def setUpTestData(cls):
        users = factories.UserFactory.create_batch(size=100)
        questions = []
        for user in users:
            questions += factories.QuestionFactory.create_batch(size=2, owner=user)
        for question in questions:
            factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(users))

    def test_detail(self):
        """Test the user answer list endpoint
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-answers', kwargs={'pk': user.pk}))
        self.assert_items_equal(response)

    def test_detail_multiple(self):
        """Test the user answer endpoint for multiple ids.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('user-answers', kwargs={'pk': ';'.join(str(user.pk) for user in users)}))
        self.assert_items_equal(response)

    def test_sort_by_activity(self):
        """Test the answer list endpoint sorted by activity date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'activity', 'order': 'asc'}
        )
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(
            reverse('user-answers', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'activity', 'order': 'desc'}
        )
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the answer list endpoint sorted by creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'order': 'asc'}
        )
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(
            reverse('user-answers', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'order': 'desc'}
        )
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the answer list endpoint sorted by votes.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'order': 'asc'}
        )
        self.assert_sorted(response, 'score')

        response = self.client.get(
            reverse('user-answers', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'order': 'desc'}
        )
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the answer list endpoint range by activity.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the answer list endpoint range by user creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the answer list endpoint range by votes.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = 10
        max_value = 1000
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'score', min_value, max_value)
