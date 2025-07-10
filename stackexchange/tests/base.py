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

    def assert_items_sorted(
        self, response, attribute: str, order: enums.OrderingDirection, field_type: enums.OrderingFieldType
    ):
        """Assert that the response items are sorted by a field.

        :param response: The response.
        :param attribute: The sorting attribute.
        :param order: The sorting order.
        :param field_type: The field type.
        """
        values = [field_type.transform(item[attribute]) for item in response.json()['items']]
        self.assertListEqual(values, sorted(values, reverse=order == enums.OrderingDirection.DESC))

    def assert_items_in_range(
        self, response, attribute: str, field_type: enums.OrderingFieldType, min_value=None, max_value=None
    ):
        """Assert that the response items fall in the provided range.

        :param response: The response.
        :param attribute: The range attribute.
        :param min_value: The minimum value.
        :param max_value: The minimum value.
        :param field_type: The field type.
        """
        for item in response.json()['items']:
            value = field_type.transform(item[attribute])
            if min_value is not None:
                self.assertLessEqual(min_value, value)
            if max_value is not None:
                self.assertGreaterEqual(max_value, value)

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

    def assert_badge_with_award_count_response(self, response):
        """Assert that the badge with award count response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            badge = models.Badge.objects.get(id=item['badge_id'])
            self.assertEqual(item['badge_type'], enums.BadgeType(badge.badge_type).value)
            self.assertEqual(item['rank'], enums.BadgeRank(badge.rank).value)
            self.assertEqual(item['award_count'],  models.UserBadge.objects.filter(badge=badge).count())
            self.assertEqual(item['name'], badge.name)
