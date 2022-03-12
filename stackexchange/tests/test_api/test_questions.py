"""Questions view set testing
"""
import dateutil.parser
import random

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
        factories.QuestionFactory.create_batch(size=1000)

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

    def test_list_sort_by_activity(self):
        """Test the question list sorted by activity date.
        """
        response = self.client.get(reverse('question-list'), data={'sort': 'activity', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('question-list'), data={'sort': 'activity', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_list_sort_by_creation(self):
        """Test the question list sorted by creation date.
        """
        response = self.client.get(reverse('question-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('question-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_list_sort_by_votes(self):
        """Test the question list sorted by votes.
        """
        response = self.client.get(reverse('question-list'), data={'sort': 'votes', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['score'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('question-list'), data={'sort': 'votes', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['score'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_detail(self):
        """Test the question detail endpoint.
        """
        # Test getting one question
        question = random.sample(list(models.Post.objects.all()), 1)[0]
        response = self.client.get(reverse('question-detail', kwargs={'pk': question.pk}))
        self.assertEqual(response.json()['items'][0]['question_id'], question.pk)

    def test_detail_multiple(self):
        """Test the question detail endpoint for multiple ids.
        """
        # Test getting multiple questions
        questions = random.sample(list(models.Post.objects.all()), 3)
        response = self.client.get(reverse('question-detail', kwargs={
            'pk': ';'.join(str(question.pk) for question in questions)
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual({row['question_id'] for row in response.json()['items']},
                            {question.pk for question in questions})
