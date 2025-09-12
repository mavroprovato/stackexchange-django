"""Tag synonym view set testing
"""
from django.urls import reverse
from rest_framework import status

from stackexchange import enums
from stackexchange.tests import base, factories


class TagSynonymsTests(base.BaseTestCase):
    """Tag synonyms view set tests.
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        factories.TagSynonymFactory.create_batch(size=100)

    def test(self):
        """Test the tag synonym endpoint.
        """
        response = self.client.get(reverse('api-tag-synonyms'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_synonym_response(response)

    def test_sort_by_creation(self):
        """Test the tag synonym endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-tag-synonyms'), data={'sort': 'creation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_tag_synonym_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_applied(self):
        """Test the tag synonym endpoint sorted by applied count.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-tag-synonyms'), data={'sort': 'applied', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_tag_synonym_response(response)
            self.assert_items_sorted(response, 'applied_count', order, enums.OrderingFieldType.INTEGER)

    def test_sort_by_activity(self):
        """Test the tag synonym endpoint sorted by last activity date.
        """
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse('api-tag-synonyms'), data={'sort': 'activity', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_tag_synonym_response(response)
            self.assert_items_sorted(response, 'last_applied_date', order, enums.OrderingFieldType.DATE)

    def test_range_by_creation(self):
        """Test tag synonym endpoint range by creation date.
        """
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(reverse('api-tag-synonyms'), data={
            'sort': 'creation', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_synonym_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_applied(self):
        """t tag synonym endpoint range by applied count.
        """
        min_value, max_value = self.generate_random_integers()
        response = self.client.get(reverse('api-tag-synonyms'), data={
            'sort': 'applied', 'min': min_value, 'max': max_value
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_synonym_response(response)
        self.assert_items_in_range(response, 'applied_count', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_range_by_activity(self):
        """Test tag synonym endpoint range by activity date.
        """
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(reverse('api-answer-list'), data={
            'sort': 'activity', 'min': min_value.isoformat(), 'max': max_value.isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_synonym_response(response)
        self.assert_items_in_range(response, 'last_applied_date', enums.OrderingFieldType.DATE, min_value, max_value)
