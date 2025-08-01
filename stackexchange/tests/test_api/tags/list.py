"""Tag view set list testing
"""
from django.urls import reverse
from rest_framework import status

from stackexchange import models, enums
from stackexchange.tests import base, factories


class TagListTests(base.BaseTestCase):
    """Tag view set list tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        factories.TagFactory.create_batch(size=10)

    def test(self):
        """Test tag list endpoint
        """
        response = self.client.get(reverse('api-tag-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)

    def test_sort_by_popular(self):
        """Test the tag list endpoint sorted by tag count.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-tag-list'), data={'sort': 'popular', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_tag_response(response)
            self.assert_items_sorted(response, 'count', order, enums.OrderingFieldType.INTEGER)

    def test_sort_by_name(self):
        """Test the tag list endpoint sorted by tag name.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-tag-list'), data={'sort': 'name', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_tag_response(response)
            self.assert_items_sorted(response, 'name', order, enums.OrderingFieldType.STRING)

    def test_range_by_popular(self):
        """Test the tag list endpoint range by badge rank.
        """
        min_value, max_value = self.generate_random_integers()
        response = self.client.get(
            reverse('api-tag-list'), data={'sort': 'popular', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)
        self.assert_items_in_range(response, 'award_count', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_range_by_name(self):
        """Test the tag list endpoint range by badge type.
        """
        min_value = 'k'
        max_value = 't'
        response = self.client.get(reverse('api-badge-list'), data={'sort': 'name', 'min': min_value, 'max': max_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)
        self.assert_items_in_range(response, 'name', enums.OrderingFieldType.STRING, min_value, max_value)

    def test_in_name(self):
        """Test the in name filter for the tag list endpoint.
        """
        # Create a user that will surely be returned
        tag = factories.TagFactory.create(name='test')
        query = 'es'
        response = self.client.get(reverse('api-tag-list'), data={'inname': query})
        self.assert_tag_response(response)
        self.assertIn(tag.id, [models.Tag.objects.get(name=row['name']).pk for row in response.json()['items']])
