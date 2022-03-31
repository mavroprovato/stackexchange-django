"""Base answer test case.
"""
from stackexchange import enums, models
from ..base import BaseTestCase


class BaseAnswerTestCase(BaseTestCase):
    """Base answer API test case
    """
    def assert_items_equal(self, response, **kwargs):
        """Assert that the items returned by the response are the same as the database items.
        """
        return super().assert_items_equal(response, models.Post, 'answer_id', attributes={
            # 'is_accepted': 'is_accepted',
            'score': 'score',
            'last_activity_date': lambda x: x.last_activity_date.isoformat().replace('+00:00', 'Z'),
            'creation_date': lambda x: x.creation_date.isoformat().replace('+00:00', 'Z'),
            'question_id': 'question_id',
            'content_license': lambda x: enums.ContentLicense[x.content_license].name,
        })
