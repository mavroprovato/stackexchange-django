"""Base question test case.
"""

from stackexchange import enums, models
from ..base import BaseTestCase


class BaseQuestionTestCase(BaseTestCase):
    """Base question API test case
    """
    def assert_items_equal(self, response, model_class=models.Post, obj_filter: str | dict = 'question_id',
                           multiple: bool = False, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if attributes is None:
            attributes = {
                'tags': lambda x: {pt.tag.name for pt in x.tags.all()},
                'owner.reputation': lambda x: x.owner.reputation,
                'owner.user_id': lambda x: x.owner.pk,
                'owner.display_name': lambda x: x.owner.display_name,
                'is_answered': lambda x: x.answer_count and x.answer_count > 1,
                'view_count': 'view_count',
                'accepted_answer_id': 'accepted_answer_id',
                'score': 'score',
                'last_activity_date': lambda x: x.last_activity_date.isoformat().replace('+00:00', 'Z'),
                'creation_date': lambda x: x.creation_date.isoformat().replace('+00:00', 'Z'),
                'last_edit_date': lambda x: x.last_edit_date.isoformat().replace('+00:00', 'Z') if x else None,
                'content_license': lambda x: enums.ContentLicense[x.content_license].name,
                'title': 'title',
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)
