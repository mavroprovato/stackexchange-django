"""Tag view set required testing
"""
import random

from django.urls import reverse

from stackexchange.tests import factories
from .base import BaseTagTestCase


class TagRequiredTests(BaseTagTestCase):
    """Tag view set required tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.TagFactory.create_batch(size=10, required=random.choice([True, False]))

    def test(self):
        """Test the tag required endpoint.
        """
        # Test getting one tag
        response = self.client.get(reverse('tag-required'))
        self.assert_items_equal(response)
        self.assertTrue(all(row['is_required'] for row in response.json()['items']))

    def test_sort_by_popular(self):
        """Test the tag required endpoint sorted by tag count.
        """
        response = self.client.get(reverse('tag-required'))
        self.assert_sorted(response, 'count')

        response = self.client.get(reverse('tag-required'))
        self.assert_sorted(response, 'count', reverse=True)

    def test_sort_by_name(self):
        """Test the tag required endpoint sorted by tag name.
        """
        response = self.client.get(reverse('tag-required'))
        self.assert_sorted(response, 'name')

        response = self.client.get(reverse('tag-required'))
        self.assert_sorted(response, 'name', reverse=True)

    def test_range_by_popular(self):
        """Test the tag required endpoint range by badge rank.
        """
        min_value = 10
        max_value = 1000
        response = self.client.get(reverse('tag-required'))
        self.assert_range(response, 'popular', min_value, max_value)

    def test_range_by_name(self):
        """Test the tag required endpoint range by badge type.
        """
        min_value = 'b'
        max_value = 'x'
        response = self.client.get(reverse('tag-required'))
        self.assert_range(response, 'popular', min_value, max_value)
