"""Tag view set list testing
"""
import unittest

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from .base import BaseTagTestCase


class TagListTests(BaseTagTestCase):
    """Tag view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.TagFactory.create_batch(size=10)

    def test(self):
        """Test tag list endpoint
        """
        # Test that the list endpoint returns successfully
        response = self.client.get(reverse('tag-list'))
        self.assert_items_equal(response)

    def test_sort_by_popular(self):
        """Test the tag list endpoint sorted by tag count.
        """
        response = self.client.get(reverse('tag-list'), data={'sort': 'popular', 'order': 'asc'})
        self.assert_sorted(response, 'count')

        response = self.client.get(reverse('tag-list'), data={'sort': 'popular', 'order': 'desc'})
        self.assert_sorted(response, 'count', reverse=True)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_sort_by_name(self):
        """Test the tag list endpoint sorted by tag name.
        """
        response = self.client.get(reverse('tag-list'), data={'sort': 'name', 'order': 'asc'})
        self.assert_sorted(response, 'name')

        response = self.client.get(reverse('tag-list'), data={'sort': 'name', 'order': 'desc'})
        self.assert_sorted(response, 'name', reverse=True)

    def test_range_by_popular(self):
        """Test the tag list endpoint range by badge rank.
        """
        min_value = 3000
        max_value = 6000
        response = self.client.get(reverse('tag-list'), data={'sort': 'popular', 'min': min_value, 'max': max_value})
        self.assert_range(response, 'count', min_value, max_value)

    def test_range_by_name(self):
        """Test the tag list endpoint range by badge type.
        """
        min_value = 'k'
        max_value = 't'
        response = self.client.get(reverse('tag-list'), data={
            'sort': 'name', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'name', min_value, max_value)

    def test_in_name(self):
        """Test the in name filter for the tag list endpoint.
        """
        # Create a user that will surely be returned
        tag = factories.TagFactory.create(name='test')
        query = 'es'
        response = self.client.get(reverse('tag-list'), data={'inname': query})
        self.assert_in_string(response, 'name', query=query)
        self.assertIn(tag.id, [models.Tag.objects.get(name=row['name']).pk for row in response.json()['items']])
