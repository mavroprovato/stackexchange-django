"""Question tagged tests
"""
import http
import random

from django.test import TestCase
from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories


class QuestionTaggedTests(TestCase):
    """Question tagged tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        tags = factories.TagFactory.create_batch(size=10)
        questions = factories.QuestionFactory.create_batch(size=100)
        for question in questions:
            question_tags = random.sample(tags, 3)
            for question_tag in question_tags:
                factories.QuestionTagFactory.create(post=question, tag=question_tag)

    def test(self):
        """Test the question list
        """
        tag = random.choice(models.Tag.objects.all())
        response = self.client.get(reverse('web-question-tagged', kwargs={'tag': tag.name}))
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
