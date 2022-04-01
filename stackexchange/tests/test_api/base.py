"""Base test classes
"""
from rest_framework import status
from rest_framework.test import APITestCase


class BaseTestCase(APITestCase):
    """Base API test case
    """
    def assert_items_equal(self, response, model_class, pk_attr, attributes: dict):
        """Assert that the items returned by the response are the same as the database items.

        :param response: The response.
        :param model_class: The model class.
        :param pk_attr: The primary key attribute in the response.
        :param attributes: A dictionary with the items to check.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.json()['items']:
            if isinstance(pk_attr, str):
                obj = model_class.objects.get(pk=row[pk_attr])
            elif isinstance(pk_attr, dict):
                obj = model_class.objects.get(**{name: row[value] for name, value in pk_attr.items()})
            else:
                raise ValueError(f"pk attr is of unsupported class: {type(pk_attr)}")
            for attribute, value in attributes.items():
                if callable(value):
                    expected_value = value(obj)
                else:
                    expected_value = getattr(obj, value)
                attribute_path = attribute.split('.')
                source_value = row[attribute_path[0]]
                for attr in attribute_path[1:]:
                    source_value = source_value[attr]
                self.assertEqual(source_value, expected_value)

    def assert_sorted(self, response, attr: str, transform=None, reverse=False):
        """Assert that the response is sorted.

        :param response: The response.
        :param attr: The attribute to check for sorting.
        :param transform: Function used to transform the values.
        :param reverse: True if the response should be reverse sorted, false otherwise.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attribute_values = [transform(row[attr]) if transform else row[attr] for row in response.json()['items']]
        self.assertListEqual(attribute_values, sorted(attribute_values, reverse=reverse))

    def assert_range(self, response, attr: str, transform=None, min_value=None, max_value=None):
        """Assert that the response is falls within a range.

        :param response: The response.
        :param attr: The attribute to check for range.
        :param transform: Function used to transform the values.
        :param min_value: The minimum value.
        :param max_value: The maximum value.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if min_value:
            self.assertTrue(
                all(transform(row[attr]) if transform else row[attr] >= min_value)
                for row in response.json()['items']
            )
        if max_value:
            self.assertTrue(
                all(transform(row[attr]) if transform else row[attr] <= max_value)
                for row in response.json()['items']
            )

    def assert_in_string(self, response, attr: str, query: str):
        """Assert that the response contains the string in the provided attribute.

        :param response: The response.
        :param attr: The attribute to check that contains the string.
        :param query: The string to check.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(query in row[attr] for row in response.json()['items']))
