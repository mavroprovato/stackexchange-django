"""Base post test case.
"""
from stackexchange import enums, models
from ..base import BaseTestCase


class BasePostTestCase(BaseTestCase):
    """Base post API test case
    """
    def assert_items_equal(self, response, **kwargs):
        """Assert that the items returned by the response are the same as the database items.
        """
        return super().assert_items_equal(response, models.Post, 'post_id', attributes={
            'score': 'score',
            'last_activity_date': lambda x: x.last_activity_date.isoformat().replace('+00:00', 'Z'),
            'creation_date': lambda x: x.creation_date.isoformat().replace('+00:00', 'Z'),
            'post_type': lambda x: enums.PostType(x.type).name.lower(),
            'content_license': lambda x: enums.ContentLicense[x.content_license].name,
        })
