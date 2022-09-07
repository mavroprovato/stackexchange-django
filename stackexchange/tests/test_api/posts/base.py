"""Base post test case.
"""

from stackexchange import enums, models
from ..base import BaseTestCase


class BasePostTestCase(BaseTestCase):
    """Base post API test case
    """
    def assert_items_equal(self, response, model_class=models.Post, obj_filter: str | dict = 'post_id',
                           multiple: bool = False, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if attributes is None:
            attributes = {
                'owner.reputation': lambda x: x.owner.reputation,
                'owner.user_id': lambda x: x.owner.pk,
                'owner.display_name': lambda x: x.owner.display_name,
                'score': 'score',
                'last_activity_date': lambda x: x.last_activity_date.isoformat().replace('+00:00', 'Z'),
                'creation_date': lambda x: x.creation_date.isoformat().replace('+00:00', 'Z'),
                'post_type': lambda x: enums.PostType(x.type).name.lower(),
                'content_license': lambda x: enums.ContentLicense[x.content_license].name,
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)


class BasePostRevisionTestCase(BaseTestCase):
    """Base post revision API test case
    """
    def assert_items_equal(self, response, model_class=models.PostHistory, obj_filter: str | dict = None,
                           multiple: bool = True, attributes: dict = None):
        """Assert that the items returned by the response are the same as the database items.
        """
        if obj_filter is None:
            obj_filter = {'revision_guid': 'revision_guid'}
        if attributes is None:
            attributes = {
                'set_community_wiki':
                    lambda x: enums.PostHistoryType(x.type).value == enums.PostHistoryType.COMMUNITY_OWNED.value,
                'is_rollback': lambda x: enums.PostHistoryType(x.type).rollback(),
                'creation_date': lambda x: x.creation_date.isoformat().replace('+00:00', 'Z'),
                'post_id': lambda x: x.post.pk,
                'post_type': lambda x: enums.PostType(x.post.type).name.lower(),
                'revision_type':
                    lambda x: 'vote_based' if enums.PostHistoryType(x.type).vote_based() else 'single_user',
                'comment': 'comment'
            }

        return super().assert_items_equal(response, model_class, obj_filter, multiple, attributes)
