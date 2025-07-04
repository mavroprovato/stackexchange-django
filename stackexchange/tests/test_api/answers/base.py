
import dateutil.parser

from stackexchange import models
from stackexchange.tests import base


class BaseAnswerTests(base.BaseTestCase):
    """Base class for testing answers.
    """
    def assert_response_schema(self, item: dict):
        """Assert that the response schema is correct.

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
