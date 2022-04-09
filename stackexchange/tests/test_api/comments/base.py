"""Base comment test case.
"""
import typing

from stackexchange import enums, models
from ..base import BaseTestCase


class BaseCommentTestCase(BaseTestCase):
    """Base comment API test case
    """
    def assert_items_equal(self, response, model_class: typing.ClassVar = models.Comment,
                           obj_filter: typing.Union[str, dict] = 'comment_id', multiple: bool = False,
                           attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if attributes is None:
            attributes = {
                'owner.reputation': lambda x: x.user.reputation,
                'owner.user_id': lambda x: x.user.pk,
                'owner.display_name': lambda x: x.user.display_name,
                'score': 'score',
                'creation_date': lambda x: x.creation_date.isoformat().replace('+00:00', 'Z'),
                'post_id': lambda x: x.post_id,
                'content_license': lambda x: enums.ContentLicense[x.content_license].name,
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)
