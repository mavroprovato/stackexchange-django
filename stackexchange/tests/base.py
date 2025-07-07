"""Base test case
"""
import dateutil.parser
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from stackexchange import enums, models


class BaseTestCase(TenantTestCase):
    """Base test case
    """
    def setUp(self):
        """Set up the multitenant test client.
        """
        self.client = TenantClient(self.tenant)

    def assert_items_sorted(self, response, attribute: str, order: enums.OrderingDirection):
        """Assert that the response items are sorted by attribute.

        :param response: The response.
        :param attribute: The sorting attribute.
        :param order: The sorting order.
        """
        values = [item[attribute] for item in response.json()['items']]
        self.assertListEqual(values, sorted(values, reverse=order == enums.OrderingDirection.DESC))

    def assert_items_in_range(self, response, attribute: str, min_value, max_value):
        """Assert that the response items fall in the provided range.

        :param response: The response.
        :param attribute: The range attribute.
        :param min_value: The minimum value.
        :param max_value: The minimum value.
        """
        for item in response.json()['items']:
            self.assertTrue(min_value <= item[attribute] <= max_value)

    def assert_answer_response(self, response):
        """Assert that the answer response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            answer = models.Post.objects.get(id=item['answer_id'])
            self.assertEqual(item['owner']['reputation'], answer.owner.reputation)
            self.assertEqual(item['owner']['user_id'], answer.owner.id)
            self.assertEqual(item['owner']['display_name'], answer.owner.display_name)
            self.assertEqual(item['owner']['user_type'], answer.owner.user_type())
            self.assertEqual(item['score'], answer.score)
            self.assertEqual(dateutil.parser.parse(item['last_activity_date']), answer.last_activity_date)
            self.assertEqual(dateutil.parser.parse(item['creation_date']), answer.creation_date)
            self.assertEqual(item['question_id'], answer.question_id)
            self.assertEqual(item['content_license'], answer.content_license)
