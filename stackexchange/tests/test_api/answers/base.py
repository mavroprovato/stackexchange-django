"""Base answer test case.
"""
from stackexchange import enums, models
from ..base import BaseTestCase


class BaseAnswerTestCase(BaseTestCase):
    """Base answer API test case
    """
    def assert_items_equal(self, response, model_class=models.Post, obj_filter: str | dict = 'answer_id',
                           multiple: bool = False, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if attributes is None:
            attributes = {
                'owner.reputation': lambda x: x.owner.reputation,
                'owner.user_id': lambda x: x.owner.pk,
                'owner.display_name': lambda x: x.owner.display_name,
                'is_accepted': lambda x: bool(x.accepted_answer_id),
                'score': 'score',
                'last_activity_date': lambda x: x.last_activity_date.isoformat().replace('+00:00', 'Z'),
                'creation_date': lambda x: x.creation_date.isoformat().replace('+00:00', 'Z'),
                'question_id': 'question_id',
                'content_license': lambda x: enums.ContentLicense[x.content_license].name,
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)
