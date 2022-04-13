"""Users API questions unaccepted testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from ..questions.base import BaseQuestionTestCase


class UserQuestionUnansweredTests(BaseQuestionTestCase):
    """Users view set question unanswered tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=100)
        for user in users:
            answer_count = random.randint(0, 3)
            question = factories.QuestionFactory.create(owner=user, answer_count=answer_count)
            answer_users = random.sample(users, answer_count)
            answers = [
                factories.AnswerFactory.create(question=question, owner=answer_user) for answer_user in answer_users
            ]
            if answers and random.choice([True, False]):
                question.accepted_answer = random.choice(answers)

    def test(self):
        """Test user questions unaccepted endpoint
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-questions-unaccepted', kwargs={'pk': user.pk}))
        self.assert_items_equal(response)
        self.assertTrue(row['answer_count'] > 0 for row in response.json()['items'])
        self.assertTrue(row['accepted_answer_id'] is None for row in response.json()['items'])

    def test_multiple(self):
        """Test the user questions unaccepted endpoint for multiple ids.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('user-questions-unaccepted', kwargs={'pk': ';'.join(str(user.pk) for user in users)})
        )
        self.assert_items_equal(response)
        self.assertTrue(row['answer_count'] > 0 for row in response.json()['items'])
        self.assertTrue(row['accepted_answer_id'] is None for row in response.json()['items'])

    def test_sort_by_activity(self):
        """Test the user questions unaccepted endpoint sorted by activity date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('user-questions-unaccepted', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'activity', 'order': 'asc'}
        )
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(
            reverse('user-questions-unaccepted', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'activity', 'order': 'desc'}
        )
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the user questions unaccepted endpoint sorted by creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('user-questions-unaccepted', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'order': 'asc'}
        )
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(
            reverse('user-questions-unaccepted', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'order': 'desc'}
        )
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the user questions unaccepted endpoint sorted by votes.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('user-questions-unaccepted', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'order': 'asc'}
        )
        self.assert_sorted(response, 'score')

        response = self.client.get(
            reverse('user-questions-unaccepted', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'order': 'desc'}
        )
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the user questions unaccepted endpoint range by activity.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('user-questions-unaccepted', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the user questions unaccepted endpoint range by user creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('user-questions-unaccepted', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the user questions unaccepted endpoint range by votes.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = 3000
        max_value = 6000
        response = self.client.get(
            reverse('user-questions-unaccepted', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'score', min_value, max_value)
