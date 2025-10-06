"""Search view set testing
"""
import datetime
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums
from stackexchange.tests import base, factories


class SearchTests(base.BaseTestCase):
    """Search view set tests
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
        """Test search endpoint
        """
        tag = random.choice(self.tags)
        response = self.client.get(reverse('api-search-list'), data={'tagged': tag.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)

    def test_sort_by_activity(self):
        """Test the search endpoint sorted by activity date.
        """
        for order in enums.OrderingDirection:
            tag = random.choice(self.tags)
            response = self.client.get(
                reverse('api-search-list'), data={'tagged': tag.name, 'sort': 'activity', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_question_response(response)
            self.assert_items_sorted(response, 'last_activity_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_creation(self):
        """Test the search endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            tag = random.choice(self.tags)
            response = self.client.get(
                reverse('api-search-list'), data={'tagged': tag.name, 'sort': 'creation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_question_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_votes(self):
        """Test the search endpoint sorted by votes.
        """
        for order in enums.OrderingDirection:
            tag = random.choice(self.tags)
            response = self.client.get(reverse('api-search-list'), data={
                'tagged': tag.name, 'sort': 'votes', 'order': order.value
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_question_response(response)
            self.assert_items_sorted(response, 'score', order, enums.OrderingFieldType.INTEGER)

    def test_range_by_activity(self):
        """Test the search endpoint range by activity.
        """
        tag = random.choice(self.tags)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(reverse('api-search-list'), data={
            'tagged': tag.name, 'sort': 'activity', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        self.assert_items_in_range(response, 'last_activity_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_creation(self):
        """Test the search endpoint range by user creation date.
        """
        tag = random.choice(self.tags)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(reverse('api-search-list'), data={
            'tagged': tag.name, 'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_votes(self):
        """Test the search endpoint range by votes.
        """
        tag = random.choice(self.tags)
        min_value, max_value = self.generate_random_integers()
        response = self.client.get(reverse('api-search-list'), data={
            'tagged': tag.name, 'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        self.assert_items_in_range(response, 'score', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_tagged_single(self):
        """Test the search endpoint filter by a single tag.
        """
        tag = random.choice(self.tags)
        response = self.client.get(reverse('api-search-list'), data={'tagged': tag.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        for row in response.json()['items']:
            self.assertIn(tag.name, row['tags'])

    def test_tagged_multiple(self):
        """Test the search endpoint filter by tags.
        """
        tags = random.sample(self.tags, 2)
        response = self.client.get(reverse('api-search-list'), data={'tagged': ';'.join(tag.name for tag in tags)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        for row in response.json()['items']:
            for tag in tags:
                self.assertIn(tag.name, row['tags'])

    def test_not_tagged(self):
        """Test the search endpoint filter by not tagged.
        """
        tag = random.choice(self.tags)
        response = self.client.get(reverse('api-search-list'), data={'tagged': tag.name, 'nottagged': tag.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        for row in response.json()['items']:
            self.assertNotIn(tag.name, row['tags'])

    def test_in_title(self):
        """Test the search endpoint in title filter.
        """
        question = factories.QuestionFactory.create(title='test')
        response = self.client.get(reverse('api-search-list'), data={'intitle': 'test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_question_response(response)
        self.assertIn(question.pk, [row['question_id'] for row in response.json()['items']])
