"""Base question test case.
"""
from stackexchange import enums, models
from ..base import BaseTestCase


class BaseQuestionTestCase(BaseTestCase):
    """Base question API test case
    """
    def assert_items_equal(self, response, **kwargs):
        """Assert that the items returned by the response are the same as the database items.
        """
        return super().assert_items_equal(response, models.Post, 'question_id', attributes={
            'is_answered': lambda x: x.answer_count and x.answer_count > 1,
            'view_count': 'view_count',
            'accepted_answer_id': 'accepted_answer_id',
            'score': 'score',
            'last_activity_date': lambda x: x.last_activity_date.isoformat().replace('+00:00', 'Z'),
            'creation_date': lambda x: x.creation_date.isoformat().replace('+00:00', 'Z'),
            'last_edit_date': lambda x: x.last_edit_date.isoformat().replace('+00:00', 'Z') if x else None,
            'content_license': lambda x: enums.ContentLicense[x.content_license].name,
            'title': 'title',
        })