"""Tests for the answers detail view.
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class AnswerRetrieveTests(base.BaseTestCase):
    """Answer view set detail tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=10)
        questions = []
        for site_user in site_users:
            questions += factories.QuestionFactory.create_batch(size=2, owner=site_user)
        for question in questions:
            factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(site_users))

    def test(self):
        """Test the answer detail endpoint
        """
        answer = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 1)[0]
        response = self.client.get(reverse('api-answer-detail', kwargs={'pk': answer.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)

    def test_multiple(self):
        """Test the answer detail endpoint for multiple ids.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)

    def test_sort_by_activity(self):
        """Test the answer detail endpoint sorted by activity date.
        """
        for order in enums.OrderingDirection:
            answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
            response = self.client.get(
                reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
                data={'sort': 'activity', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'last_activity_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_creation_date(self):
        """Test the answer detail endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
            response = self.client.get(
                reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
                data={'sort': 'creation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_votes(self):
        """Test the answer detail endpoint sorted by votes.
        """
        for order in enums.OrderingDirection:
            answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
            response = self.client.get(
                reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
                data={'sort': 'votes', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'score', order, enums.OrderingFieldType.INTEGER)

    def test_range_by_activity(self):
        """Test the answer detail endpoint range by activity.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'activity', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'last_activity_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the answer detail endpoint range by creation date.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_votes(self):
        """Test the answer detail endpoint range by votes.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        min_value = 3000
        max_value = 6000
        response = self.client.get(
            reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'score', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_date_range(self):
        """Test the answer detail list endpoint date range.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        from_date, to_date = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}), data={
                'fromdate': from_date.isoformat(), 'todate': to_date.isoformat()
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, from_date, to_date)
