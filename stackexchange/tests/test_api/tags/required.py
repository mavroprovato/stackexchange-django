"""Tag view set required testing
"""
from django.urls import reverse
from rest_framework import status

from stackexchange import enums
from stackexchange.tests import base, factories


class TagRequiredTests(base.BaseTestCase):
    """Tag view set required tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        factories.TagFactory.create_batch(size=10)

    def test(self):
        """Test the tag required endpoint.
        """
        response = self.client.get(reverse('api-tag-required'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)
        self.assertTrue(all(item['is_required'] for item in response.json()['items']))

    def test_multiple(self):
        """Test the tag required endpoint for multiple ids.
        """
        response = self.client.get(reverse('api-tag-required'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)
        self.assertTrue(all(item['is_required'] for item in response.json()['items']))

    def test_sort_by_popular(self):
        """Test the tag required endpoint sorted by tag count.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-tag-required'), data={'sort': 'popular', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_tag_response(response)
            self.assertTrue(all(item['is_required'] for item in response.json()['items']))
            self.assert_items_sorted(response, 'count', order, enums.OrderingFieldType.INTEGER)

    def test_sort_by_name(self):
        """Test the tag required endpoint sorted by tag name.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(reverse('api-tag-required'), data={'sort': 'name', 'order': order.value})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_tag_response(response)
            self.assertTrue(all(item['is_required'] for item in response.json()['items']))
            self.assert_items_sorted(response, 'name', order, enums.OrderingFieldType.STRING)

    def test_range_by_popular(self):
        """Test the tag required endpoint range by badge rank.
        """
        min_value, max_value = self.generate_random_integers()
        response = self.client.get(
            reverse('api-tag-required'), data={'sort': 'popular', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)
        self.assertTrue(all(item['is_required'] for item in response.json()['items']))
        self.assert_items_in_range(response, 'count', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_range_by_name(self):
        """Test the tag required endpoint range by badge type.
        """
        min_value = 'k'
        max_value = 't'
        response = self.client.get(
            reverse('api-tag-required'), data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)
        self.assertTrue(all(item['is_required'] for item in response.json()['items']))
        self.assert_items_in_range(response, 'name', enums.OrderingFieldType.STRING, min_value, max_value)
