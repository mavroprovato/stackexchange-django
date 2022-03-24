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
