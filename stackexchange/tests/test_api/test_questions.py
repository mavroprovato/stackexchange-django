"""Questions view set testing
"""
import dateutil.parser

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .. import factories
from stackexchange import enums, models


class QuestionTests(APITestCase):
    """Question view set tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.QuestionAnswerFactory.create_batch(size=1000)

    def test_list(self):
        """Test question list endpoint
        """
        response = self.client.get(reverse('question-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for row in response.json()['items']:
            question = models.Post.objects.get(pk=row['question_id'])
            self.assertEqual(row['view_count'], question.view_count)
            self.assertEqual(row['answer_count'], question.answer_count)
            self.assertEqual(row['score'], question.score)
            self.assertEqual(dateutil.parser.parse(row['last_activity_date']), question.last_activity_date)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), question.creation_date)
            self.assertEqual(dateutil.parser.parse(row['last_edit_date']), question.last_edit_date)
            self.assertEqual(row['content_license'], enums.ContentLicense[question.content_license].name)
            self.assertEqual(row['title'], question.title)

    def test_no_answers(self):
        """Test question with no answer endpoint
        """
        response = self.client.get(reverse('question-no-answers'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
