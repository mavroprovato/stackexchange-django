"""Tag view set info testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import models, enums
from stackexchange.tests import base, factories


class TagInfoTests(base.BaseTestCase):
    """Tag view set info tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        factories.TagFactory.create_batch(size=10)

    def test(self):
        """Test the tag detail endpoint.
        """
        tag = random.sample(list(models.Tag.objects.all()), 1)[0]
        response = self.client.get(reverse('api-tag-info', kwargs={'pk': tag.name}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)

    def test_multiple(self):
        """Test the tag detail endpoint for multiple ids.
        """
        tags = random.sample(list(models.Tag.objects.all()), 3)
        response = self.client.get(reverse('api-tag-info', kwargs={'pk': ';'.join(str(tag.name) for tag in tags)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)

    def test_sort_by_popular(self):
        """Test the tag detail endpoint sorted by tag count.
        """
        tags = random.sample(list(models.Tag.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-tag-info', kwargs={'pk': ';'.join(str(tag.name) for tag in tags)}),
                data={'sort': 'popular', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_tag_response(response)
            self.assert_items_sorted(response, 'count', order, enums.OrderingFieldType.INTEGER)

    def test_sort_by_name(self):
        """Test the tag list endpoint sorted by tag name.
        """
        tags = random.sample(list(models.Tag.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-tag-info', kwargs={'pk': ';'.join(str(tag.name) for tag in tags)}),
                data={'sort': 'name', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_tag_response(response)
            self.assert_items_sorted(response, 'name', order, enums.OrderingFieldType.STRING)

    def test_range_by_popular(self):
        """Test the tag list endpoint range by badge rank.
        """
        tags = random.sample(list(models.Tag.objects.all()), 3)
        min_value, max_value = self.generate_random_integers()
        response = self.client.get(
            reverse('api-tag-info', kwargs={'pk': ';'.join(str(tag.name) for tag in tags)}),
            data={'sort': 'popular', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)
        self.assert_items_in_range(response, 'award_count', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_range_by_name(self):
        """Test the tag list endpoint range by badge type.
        """
        tags = random.sample(list(models.Tag.objects.all()), 3)
        min_value = 'k'
        max_value = 't'
        response = self.client.get(
            reverse('api-tag-info', kwargs={'pk': ';'.join(str(tag.name) for tag in tags)}),
            data={'sort': 'name', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_response(response)
        self.assert_items_in_range(response, 'name', enums.OrderingFieldType.STRING, min_value, max_value)
