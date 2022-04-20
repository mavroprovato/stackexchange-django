"""Question detail tests
"""
import http
import random

from django.test import TestCase
from django.urls import reverse

from stackexchange.tests import factories


class QuestionDetailTests(TestCase):
    """Question detail tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=20)
        question = factories.QuestionFactory.create(owner=random.choice(users))
        cls.question = question
        for _ in range(5):
            factories.CommentFactory.create(post=question, user=random.choice(users))
        answers = factories.AnswerFactory.create_batch(size=10, question=question)
        for answer in answers:
            for _ in range(5):
                factories.CommentFactory.create(post=answer, user=random.choice(users))

    def test_by_id(self):
        """Test the detail by id
        """
        response = self.client.get(reverse('web-question-detail', kwargs={'pk': self.question.pk}))
        self.assertEqual(response.status_code, http.HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('web-question-detail-slug', kwargs={
            'pk': self.question.pk, 'slug': self.question.slug()}))

    def test_by_id_and_slug(self):
        """Test the detail by id and slug
        """
        response = self.client.get(
            reverse('web-question-detail-slug', kwargs={'pk': self.question.pk, 'slug': self.question.slug()}))
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
