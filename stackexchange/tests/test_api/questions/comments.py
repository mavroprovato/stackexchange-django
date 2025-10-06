"""Question view set comments testing
"""
import datetime
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class QuestionCommentsTests(base.BaseTestCase):
    """Question view set comments tests
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
        for _ in range(1000):
            factories.PostCommentFactory.create(post=random.choice(questions), user=random.choice(site_users))

    def test(self):
        """Test question comment list endpoint
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        response = self.client.get(
            reverse('api-question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}))
        self.assert_comment_response(response)

    def test_sort_by_creation(self):
        """Test the question comments sorted by comment creation date.
        """
        for order in enums.OrderingDirection:
            questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
            response = self.client.get(
                reverse('api-question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
                data={'sort': 'creation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_comment_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_votes(self):
        """Test the question comments sorted by comment votes.
        """
        for order in enums.OrderingDirection:
            questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
            response = self.client.get(
                reverse('api-question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
                data={'sort': 'votes', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_comment_response(response)
            self.assert_items_sorted(response, 'score', order, enums.OrderingFieldType.INTEGER)

    def test_range_by_creation(self):
        """Test the comments list endpoint range by creation date.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_votes(self):
        """Test the user list endpoint range by comment score.
        """
        questions = random.sample(list(models.Post.objects.filter(type=enums.PostType.QUESTION)), 3)
        min_value, max_value = self.generate_random_integers()
        response = self.client.get(
            reverse('api-question-comments', kwargs={'pk': ';'.join(str(question.pk) for question in questions)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)
        self.assert_items_in_range(response, 'score', enums.OrderingFieldType.INTEGER, min_value, max_value)
