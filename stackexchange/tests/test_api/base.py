"""Base test classes
"""
from rest_framework import status
from rest_framework.test import APITestCase


class BaseTestCase(APITestCase):
    """Base API test case
    """
    def assert_items_equal(
            self, response, model_class, obj_filter: str | dict, multiple: bool = False, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.

        :param response: The response.
        :param model_class: The model class.
        :param obj_filter: The filter expression used to get the database object from the response.
        :param multiple: Try to get a unique item from the database if False, else get the first one.
        :param attributes: A dictionary with the items to check.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.json()['items']:
            # Get the database object
            if isinstance(obj_filter, str):
                obj = model_class.objects.filter(pk=row[obj_filter])
            elif isinstance(obj_filter, dict):
                obj = model_class.objects.filter(**{
                    name: get_attribute(row, value) for name, value in obj_filter.items()
                })
            else:
                raise ValueError(f"Object filter is of unsupported class: {type(obj_filter)}")
            obj = obj.first() if multiple else obj.get()

            # Assert that the returned values are the same as the database values
            if attributes is not None:
                for attribute, value in attributes.items():
                    if callable(value):
                        expected_value = value(obj)
                    else:
                        expected_value = getattr(obj, value)
                    source_value = get_attribute(row, attribute)
                    if isinstance(expected_value, set):
                        self.assertSetEqual(set(source_value), expected_value)
                    else:
                        self.assertEqual(source_value, expected_value)

    def assert_sorted(self, response, attr: str, transform=None, case_insensitive=False, reverse=False):
        """Assert that the response is sorted.

        :param response: The response.
        :param attr: The attribute to check for sorting.
        :param case_insensitive: True if the sort should be case-insensitive.
        :param transform: Function used to transform the values.
        :param reverse: True if the response should be reverse sorted, false otherwise.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attribute_values = [transform(row[attr]) if transform else row[attr] for row in response.json()['items']]
        if case_insensitive:
            expected_values = sorted(attribute_values, reverse=reverse, key=str.casefold)
        else:
            expected_values = sorted(attribute_values, reverse=reverse)
        self.assertListEqual(attribute_values, expected_values)

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


def get_attribute(row: dict, attribute: str):
    """Get the attribute from a dictionary. The attribute can contain periods in order to get nested attributes.

    :param row: The row.
    :param attribute: The attribute.
    :return: The dictionary value.
    """
    attribute_path = attribute.split('.')
    value = row[attribute_path[0]]
    for attr in attribute_path[1:]:
        value = value[attr]

    return value
