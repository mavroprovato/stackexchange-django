"""Base comment test case.
"""
from stackexchange import enums, models
from ..base import BaseTestCase


class BaseCommentTestCase(BaseTestCase):
    """Base comment API test case
    """
    def assert_items_equal(self, response, **kwargs):
        """Assert that the items returned by the response are the same as the database items.
        """
        return super().assert_items_equal(response, models.Comment, 'comment_id', attributes={
            'score': 'score',
            'creation_date': lambda x: x.creation_date.isoformat().replace('+00:00', 'Z'),
            'post_id': lambda x: x.post_id,
            'content_license': lambda x: enums.ContentLicense[x.content_license].name,
        })
