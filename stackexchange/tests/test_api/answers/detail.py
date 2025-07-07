"""Tests for the answers detail view.
"""
import datetime
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class AnswerDetailTests(base.BaseTestCase):
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
        """Test the question detail endpoint
        """
        answer = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 1)[0]
        response = self.client.get(reverse('api-answer-detail', kwargs={'pk': answer.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)

    def test_multiple(self):
        """Test the question detail endpoint for multiple ids.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        response = self.client.get(
            reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)

    def test_sort_by_activity(self):
        """Test the question detail endpoint sorted by activity date.
        """
        for order in enums.OrderingDirection:
            answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
            response = self.client.get(
                reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
                data={'sort': 'activity', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            values = [item['last_activity_date'] for item in response.json()['items']]
            self.assertListEqual(values, sorted(values, reverse=order == enums.OrderingDirection.DESC))

    def test_sort_by_creation_date(self):
        """Test the question detail endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
            response = self.client.get(
                reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
                data={'sort': 'creation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            values = [item['creation_date'] for item in response.json()['items']]
            self.assertListEqual(values, sorted(values, reverse=order == enums.OrderingDirection.DESC))

    def test_sort_by_votes(self):
        """Test the question detail endpoint sorted by votes.
        """
        for order in enums.OrderingDirection:
            answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
            response = self.client.get(
                reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
                data={'sort': 'votes', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            values = [item['score'] for item in response.json()['items']]
            self.assertListEqual(values, sorted(values, reverse=order == enums.OrderingDirection.DESC))

    def test_range_by_activity(self):
        """Test the question detail endpoint range by activity.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'activity', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        for item in response.json()['items']:
            self.assertTrue(min_value.isoformat() <= item['last_activity_date'] <= max_value.isoformat())

    def test_range_by_creation_date(self):
        """Test the question detail endpoint range by user creation date.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        for item in response.json()['items']:
            self.assertTrue(min_value.isoformat() <= item['creation_date'] <= max_value.isoformat())

    def test_range_by_votes(self):
        """Test the question detail endpoint range by votes.
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
        for item in response.json()['items']:
            self.assertTrue(min_value <= item['score'] <= max_value)

    def test_date_range(self):
        """Test the question detail list endpoint date range.
        """
        answers = random.sample(list(models.Post.objects.filter(type=enums.PostType.ANSWER)), 3)
        from_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        to_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-answer-detail', kwargs={'pk': ';'.join(str(answer.pk) for answer in answers)}), data={
                'fromdate': from_value.isoformat(), 'todate': to_value.isoformat()
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        for item in response.json()['items']:
            self.assertTrue(from_value.isoformat() <= item['creation_date'] <= to_value.isoformat())
