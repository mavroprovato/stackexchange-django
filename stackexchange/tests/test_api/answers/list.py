"""Tests for the answers list view.
"""
import random

import dateutil.parser
from django.urls import reverse
from rest_framework import status

from stackexchange.tests import factories
from stackexchange.tests.base import BaseTestCase
from stackexchange import models


class AnswerListTests(BaseTestCase):
    """Answer view set list tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=100)
        questions = []
        for site_user in site_users:
            questions += factories.QuestionFactory.create_batch(size=2, owner=site_user)
        for question in questions:
            factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(site_users))

    def test(self):
        """Test answer list endpoint
        """
        response = self.client.get(reverse('api-answer-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for item in response.json()['items']:
            answer = models.Post.objects.get(id=item['answer_id'])
            self.assertEqual(item['owner']['reputation'], answer.owner.reputation)
            self.assertEqual(item['owner']['user_id'], answer.owner.id)
            self.assertEqual(item['owner']['display_name'], answer.owner.display_name)
            # TODO: check user type
            self.assertEqual(item['score'], answer.score)
            self.assertEqual(dateutil.parser.parse(item['last_activity_date']), answer.last_activity_date)
            self.assertEqual(dateutil.parser.parse(item['creation_date']), answer.creation_date)
            self.assertEqual(item['question_id'], answer.question_id)
            self.assertEqual(item['content_license'], answer.content_license)
