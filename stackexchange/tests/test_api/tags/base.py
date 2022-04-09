"""Base tag test case.
"""
import typing

from stackexchange import models
from ..base import BaseTestCase


class BaseTagTestCase(BaseTestCase):
    """Base API tag test case
    """
    def assert_items_equal(self, response, model_class: typing.ClassVar = models.Tag,
                           obj_filter: typing.Union[str, dict] = None, multiple: bool = False, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if obj_filter is None:
            obj_filter = {'name': 'name'}
        if attributes is None:
            attributes = {
                'is_moderator_only': 'moderator_only',
                'is_required': 'required',
                'count': 'award_count',
                'name': 'name',
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)


class BaseTagWikiTestCase(BaseTestCase):
    """Base API tag wiki test case
    """
    def assert_items_equal(self, response, model_class: typing.ClassVar = models.Tag,
                           obj_filter: typing.Union[str, dict] = None, multiple: bool = False, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if obj_filter is None:
            obj_filter = {'name': 'tag_name'}
        if attributes is None:
            attributes = {
                'excerpt_last_edit_date':
                    lambda x: x.excerpt.last_edit_date.isoformat().replace('+00:00', 'Z') if x.excerpt else None,
                'body_last_edit_date':
                    lambda x: x.wiki.last_edit_date.isoformat().replace('+00:00', 'Z') if x.wiki else None,
                'excerpt': lambda x: x.excerpt.body if x.excerpt else None,
                'tag_name': 'name'
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)
