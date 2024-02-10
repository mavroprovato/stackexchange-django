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
        site = factories.SiteFactory.create()
        site_users = factories.SiteUserFactory.create_batch(site=site, size=20)
        question = factories.QuestionFactory.create(owner=random.choice(site_users))
        cls.question = question
        for _ in range(5):
            factories.PostCommentFactory.create(post=question, user=random.choice(site_users))
        answers = factories.AnswerFactory.create_batch(size=10, question=question)
        for answer in answers:
            for _ in range(5):
                factories.PostCommentFactory.create(post=answer, user=random.choice(site_users))

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
