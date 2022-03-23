"""Base test classes
"""
from rest_framework import status
from rest_framework.test import APITestCase


class BaseTestCase(APITestCase):
    """Base API test case
    """
    def assert_items_equal(self, response, model_class, pk_attr: str, attributes: dict):
        """Assert that the items returned by the response are the same as the database items.

        :param response: The response.
        :param model_class: The model class.
        :param pk_attr: The primary key attribute in the response.
        :param attributes: A dictionary with the items to check.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.json()['items']:
            obj = model_class.objects.get(pk=row[pk_attr])
            for attribute, value in attributes.items():
                if callable(value):
                    expected_value = value(getattr(obj, attribute))
                else:
                    expected_value = getattr(obj, attribute)
                self.assertEqual(row[attribute], expected_value)

    def assert_sorted(self, response, attr: str, reverse=False):
        """Check if the response is sorted.

        :param response: The response.
        :param attr: The attribute to check for sorting.
        :param reverse: True if the response should be reverse sorted, false otherwise.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attribute_values = [row[attr] for row in response.json()['items']]
        self.assertListEqual(attribute_values, sorted(attribute_values, reverse=reverse))
