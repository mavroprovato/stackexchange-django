"""Questions view set list testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums
from stackexchange.tests import base, factories


class QuestionListTests(base.BaseTestCase):
    """Question view set list tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=10)
        tags = factories.TagFactory.create_batch(size=5)
        cls.tags = tags
        for site_user in site_users:
            questions = factories.QuestionFactory.create_batch(size=3, owner=site_user)
            for question in questions:
                for _ in range(3):
                    factories.QuestionTagFactory(post=question, tag=random.choice(tags))

    def test(self):
        """Test question list endpoint
        """
        response = self.client.get(reverse('api-question-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)

    def test_sort_by_activity(self):
        """Test the question list endpoint sorted by activity date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-question-list'), data={'sort': 'activity', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_question_response(response)
            self.assert_items_sorted(response, 'last_activity_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_creation_date(self):
        """Test the question list endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-question-list'), data={'sort': 'creation', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_question_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_votes(self):
        """Test the question list endpoint sorted by votes.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-question-list'), data={'sort': 'votes', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_question_response(response)
            self.assert_items_sorted(response, 'score', order, enums.OrderingFieldType.INTEGER)

    def test_range_by_activity(self):
        """Test the question list endpoint range by activity date.
        """
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(reverse('api-question-list'), data={
            'sort': 'activity', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        self.assert_items_in_range(response, 'last_activity_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the question list endpoint range by creation date.
        """
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(reverse('api-question-list'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_votes(self):
        """Test the question list endpoint range by votes.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-question-list'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        self.assert_items_in_range(response, 'score', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_tagged_single(self):
        """Test the question list endpoint filter by a single tag.
        """
        tag = random.choice(self.tags)
        response = self.client.get(reverse('api-question-list'), data={'tagged': tag.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        for row in response.json()['items']:
            self.assertIn(tag.name, row['tags'])

    def test_tagged_multiple(self):
        """Test the question list endpoint filter by tags.
        """
        tags = random.sample(self.tags, 2)
        response = self.client.get(reverse('api-question-list'), data={'tagged': ';'.join(tag.name for tag in tags)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        for row in response.json()['items']:
            for tag in tags:
                self.assertIn(tag.name, row['tags'])
