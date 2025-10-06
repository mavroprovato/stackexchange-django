"""Questions view set answers testing
"""
import datetime
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class QuestionAnswerTests(base.BaseTestCase):
    """Question view set answers tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=100)
        questions = []
        for site_user in site_users:
            questions += factories.QuestionFactory.create_batch(size=3, owner=site_user)
        for question in questions:
            factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(site_users))

    def test(self):
        """Test question list endpoint
        """
        questions = random.sample(list(models.Post.objects.answers()), 3)
        response = self.client.get(
            reverse('api-question-answers', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}))
        self.assert_answer_response(response)

    def test_sort_by_activity(self):
        """Test the question answers endpoint sorted by activity date.
        """
        for order in enums.OrderingDirection:
            questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
            response = self.client.get(
                reverse('api-question-answers', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
                data={'sort': 'activity', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'last_activity_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_creation(self):
        """Test the question answers endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
            response = self.client.get(
                reverse('api-question-answers', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
                data={'sort': 'creation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_votes(self):
        """Test the question answers endpoint sorted by votes.
        """
        for order in enums.OrderingDirection:
            questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
            response = self.client.get(
                reverse('api-question-answers', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
                data={'sort': 'votes', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'score', order, enums.OrderingFieldType.INTEGER)

    def test_range_by_activity(self):
        """Test the question answers endpoint range by activity.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-question-answers', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'activity', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'last_activity_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_creation(self):
        """Test the question answers endpoint range by user creation date.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-question-answers', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_votes(self):
        """Test the question answers endpoint range by votes.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        min_value, max_value = self.generate_random_integers()
        response = self.client.get(
            reverse('api-question-answers', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'score', enums.OrderingFieldType.INTEGER, min_value, max_value)
