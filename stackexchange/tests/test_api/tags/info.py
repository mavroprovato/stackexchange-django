"""Tag view set info testing
"""
import random
import unittest

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from .base import BaseTagTestCase


class TagInfoTests(BaseTagTestCase):
    """Tag view set info tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.TagFactory.create_batch(size=10)

    def test(self):
        """Test the tag detail endpoint.
        """
        tag = random.sample(list(models.Tag.objects.all()), 1)[0]
        response = self.client.get(reverse('tag-info', kwargs={'pk': tag.name}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the tag detail endpoint for multiple ids.
        """
        # Test getting multiple tags
        tags = random.sample(list(models.Tag.objects.all()), 3)
        response = self.client.get(reverse('tag-info', kwargs={
            'pk': ';'.join(str(tag.name) for tag in tags)
        }))
        self.assert_items_equal(response)

    def test_sort_by_popular(self):
        """Test the tag detail endpoint sorted by tag count.
        """
        tags = random.sample(list(models.Tag.objects.all()), 3)
        response = self.client.get(reverse('tag-info', kwargs={
            'pk': ';'.join(str(tag.name) for tag in tags)
        }), data={'sort': 'popular', 'order': 'asc'})
        self.assert_sorted(response, 'count')

        response = self.client.get(reverse('tag-info', kwargs={
            'pk': ';'.join(str(tag.name) for tag in tags)
        }), data={'sort': 'popular', 'order': 'desc'})
        self.assert_sorted(response, 'count', reverse=True)

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_sort_by_name(self):
        """Test the tag list endpoint sorted by tag name.
        """
        tags = random.sample(list(models.Tag.objects.all()), 3)
        response = self.client.get(reverse('tag-info', kwargs={
            'pk': ';'.join(str(tag.name) for tag in tags)
        }), data={'sort': 'name', 'order': 'asc'})
        self.assert_sorted(response, 'name')

        response = self.client.get(reverse('tag-info', kwargs={
            'pk': ';'.join(str(tag.name) for tag in tags)
        }), data={'sort': 'name', 'order': 'desc'})
        self.assert_sorted(response, 'name', reverse=True)

    def test_range_by_popular(self):
        """Test the tag list endpoint range by badge rank.
        """
        min_value = 3000
        max_value = 6000
        tags = random.sample(list(models.Tag.objects.all()), 3)
        response = self.client.get(reverse('tag-info', kwargs={
            'pk': ';'.join(str(tag.name) for tag in tags)
        }), data={'sort': 'popular', 'min': min_value, 'max': max_value})
        self.assert_range(response, 'popular', min_value, max_value)

    def test_range_by_name(self):
        """Test the tag list endpoint range by badge type.
        """
        min_value = 'k'
        max_value = 't'
        tags = random.sample(list(models.Tag.objects.all()), 3)
        response = self.client.get(reverse('tag-info', kwargs={
            'pk': ';'.join(str(tag.name) for tag in tags)
        }), data={'sort': 'name', 'min': min_value, 'max': max_value})
        self.assert_range(response, 'name', min_value, max_value)
