"""Questions view set list testing
"""
import datetime
import random

from django.urls import reverse
from rest_framework import status

from stackexchange.tests import factories
from .base import BaseQuestionTestCase


class QuestionListTests(BaseQuestionTestCase):
    """Question view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        site = factories.SiteFactory.create()
        site_users = factories.SiteUserFactory.create_batch(site=site, size=10)
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
        self.assert_items_equal(response)

    def test_sort_by_activity(self):
        """Test the question list endpoint sorted by activity date.
        """
        response = self.client.get(reverse('api-question-list'), data={'sort': 'activity', 'order': 'asc'})
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(reverse('api-question-list'), data={'sort': 'activity', 'order': 'desc'})
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the question list endpoint sorted by creation date.
        """
        response = self.client.get(reverse('api-question-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(reverse('api-question-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the question list endpoint sorted by votes.
        """
        response = self.client.get(reverse('api-question-list'), data={'sort': 'votes', 'order': 'asc'})
        self.assert_sorted(response, 'score')

        response = self.client.get(reverse('api-question-list'), data={'sort': 'votes', 'order': 'desc'})
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the question list endpoint range by activity.
        """
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-question-list'), data={
            'sort': 'activity', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the question list endpoint range by user creation date.
        """
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(reverse('api-question-list'), data={
            'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the question list endpoint range by votes.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('api-question-list'), data={
            'sort': 'votes', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'score', min_value, max_value)

    def test_tagged_single(self):
        """Test the question list endpoint filter by a single tag.
        """
        tag = random.choice(self.tags)
        response = self.client.get(reverse('api-question-list'), data={'tagged': tag.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.json()['items']:
            self.assertIn(tag.name, row['tags'])

    def test_tagged_multiple(self):
        """Test the question list endpoint filter by tags.
        """
        tags = random.sample(self.tags, 2)
        response = self.client.get(reverse('api-question-list'), data={'tagged': ';'.join(tag.name for tag in tags)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.json()['items']:
            for tag in tags:
                self.assertIn(tag.name, row['tags'])
