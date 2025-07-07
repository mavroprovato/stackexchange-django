"""Base test case
"""
import dateutil.parser
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from stackexchange import models


class BaseTestCase(TenantTestCase):
    """Base test case
    """
    def setUp(self):
        """Set up the multitenant test client.
        """
        self.client = TenantClient(self.tenant)

    def assert_answer_response(self, item: dict):
        """Assert that the answer response schema is correct.

        :param item: The response item.
        """
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
