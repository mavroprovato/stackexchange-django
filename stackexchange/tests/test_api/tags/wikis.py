"""Tag view set wikis testing
"""
import random

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from .base import BaseTagWikiTestCase


class TagWikisTests(BaseTagWikiTestCase):
    """Tag view set wikis tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.TagFactory.create_batch(size=10)

    def test(self):
        """Test the tag wikis endpoint.
        """
        tag = random.sample(list(models.Tag.objects.all()), 1)[0]
        response = self.client.get(reverse('api-tag-wikis', kwargs={'pk': tag.name}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the tag wikis endpoint for multiple ids.
        """
        # Test getting multiple tags
        tags = random.sample(list(models.Tag.objects.all()), 3)
        response = self.client.get(reverse('api-tag-wikis', kwargs={
            'pk': ';'.join(str(tag.name) for tag in tags)
        }))
        self.assert_items_equal(response)
