"""Base tag test case.
"""
from stackexchange import models
from ..base import BaseTestCase


class BaseTagTestCase(BaseTestCase):
    """Base API tag test case
    """
    def assert_items_equal(self, response, **kwargs):
        """Assert that the items returned by the response are the same as the database items.
        """
        return super().assert_items_equal(response, models.Tag, {'name': 'name'}, attributes={
            'is_moderator_only': 'moderator_only',
            'is_required': 'required',
            'count': 'award_count',
            'name': 'name',
        })


class BaseTagWikiTestCase(BaseTestCase):
    """Base API tag wiki test case
    """
    def assert_items_equal(self, response, **kwargs):
        """Assert that the items returned by the response are the same as the database items.
        """
        return super().assert_items_equal(response, models.Tag, {'name': 'tag_name'}, attributes={
            'excerpt_last_edit_date':
                lambda x: x.excerpt.last_edit_date.isoformat().replace('+00:00', 'Z') if x.excerpt else None,
            'body_last_edit_date':
                lambda x: x.wiki.last_edit_date.isoformat().replace('+00:00', 'Z') if x.wiki else None,
            'excerpt': lambda x: x.excerpt.body if x.excerpt else None,
            'tag_name': 'name'
        })
