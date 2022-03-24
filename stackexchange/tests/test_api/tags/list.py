"""Tag view set list testing
"""
from django.urls import reverse

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
        min_value = 10
        max_value = 1000
        response = self.client.get(reverse('tag-list'), data={'min': min_value, 'max': max_value})
        self.assert_range(response, 'count', min_value, max_value)

    def test_range_by_name(self):
        """Test the tag list endpoint range by badge type.
        """
        min_value = 'b'
        max_value = 'x'
        response = self.client.get(reverse('tag-list'), data={
            'sort': 'name', 'min': min_value, 'max': max_value
        })
        self.assert_range(response, 'name', min_value, max_value)
