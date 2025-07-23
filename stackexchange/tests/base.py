"""Base test case
"""
import dateutil.parser
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from stackexchange import enums, models


class BaseTestCase(TenantTestCase):
    """Base test case
    """
    def setUp(self):
        """Set up the multitenant test client.
        """
        self.client = TenantClient(self.tenant)

    def assert_items_sorted(
        self, response, attribute: str, order: enums.OrderingDirection, field_type: enums.OrderingFieldType
    ):
        """Assert that the response items are sorted by a field.

        :param response: The response.
        :param attribute: The sorting attribute.
        :param order: The sorting order.
        :param field_type: The field type.
        """
        values = [field_type.transform(item[attribute]) for item in response.json()['items']]
        self.assertListEqual(values, sorted(values, reverse=order == enums.OrderingDirection.DESC))

    def assert_items_in_range(
        self, response, attribute: str, field_type: enums.OrderingFieldType, min_value=None, max_value=None
    ):
        """Assert that the response items fall in the provided range.

        :param response: The response.
        :param attribute: The range attribute.
        :param min_value: The minimum value.
        :param max_value: The minimum value.
        :param field_type: The field type.
        """
        for item in response.json()['items']:
            value = field_type.transform(item[attribute])
            if min_value is not None:
                self.assertLessEqual(min_value, value)
            if max_value is not None:
                self.assertGreaterEqual(max_value, value)

    def assert_answer_response(self, response):
        """Assert that the answer response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            answer = models.Post.objects.get(id=item['answer_id'])
            self.assertEqual(item['owner']['reputation'], answer.owner.reputation)
            self.assertEqual(item['owner']['user_id'], answer.owner.id)
            self.assertEqual(item['owner']['display_name'], answer.owner.display_name)
            self.assertEqual(item['owner']['user_type'], answer.owner.user_type())
            self.assertEqual(item['score'], answer.score)
            self.assertEqual(dateutil.parser.parse(item['last_activity_date']), answer.last_activity_date)
            self.assertEqual(dateutil.parser.parse(item['creation_date']), answer.creation_date)
            self.assertEqual(item['question_id'], answer.question_id)
            self.assertEqual(item['content_license'], answer.content_license)

    def assert_badge_with_award_count_response(self, response):
        """Assert that the badge with award count response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            badge = models.Badge.objects.get(id=item['badge_id'])
            self.assertEqual(item['badge_type'], enums.BadgeType(badge.badge_type).value)
            self.assertEqual(item['rank'], enums.BadgeRank(badge.rank).value)
            self.assertEqual(item['award_count'],  models.UserBadge.objects.filter(badge=badge).count())
            self.assertEqual(item['name'], badge.name)

    def assert_badge_with_recipient_response(self, response):
        """Assert that the badge with recipient response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            badge = models.Badge.objects.get(id=item['badge_id'])
            self.assertEqual(item['badge_type'], enums.BadgeType(badge.badge_type).value)
            self.assertEqual(item['rank'], enums.BadgeRank(badge.rank).value)
            self.assertEqual(item['name'], badge.name)
            site_user = models.SiteUser.objects.get(id=item['user']['user_id'])
            self.assertEqual(item['user']['reputation'], site_user.reputation)
            self.assertEqual(item['user']['display_name'], site_user.display_name)
            self.assertEqual(item['user']['user_type'], site_user.user_type())
            self.assertTrue(models.UserBadge.objects.filter(badge=badge, user=site_user).exists())

    def assert_comment_response(self, response):
        """Assert that the comment response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            comment = models.PostComment.objects.get(id=item['comment_id'])
            self.assertEqual(item['score'], comment.score)
            self.assertEqual(dateutil.parser.parse(item['creation_date']), comment.creation_date)
            self.assertEqual(item['post_id'], comment.post_id)
            self.assertEqual(item['content_license'], enums.ContentLicense(comment.content_license).value)
            if item['owner'] is not None:
                self.assertEqual(item['owner']['reputation'], comment.user.reputation)
                self.assertEqual(item['owner']['user_id'], comment.user_id)
                self.assertEqual(item['owner']['display_name'], comment.user.display_name)
                self.assertEqual(item['owner']['user_type'], comment.user.user_type())

    def assert_question_response(self, response):
        """Assert that the comment response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            question = models.Post.objects.get(id=item['question_id'])
            self.assertEqual(item['is_answered'], question.is_answered())
            self.assertEqual(item['view_count'], question.view_count)
            self.assertEqual(item['accepted_answer_id'], question.accepted_answer_id)
            self.assertEqual(item['answer_count'], question.answer_count)
            self.assertEqual(item['score'], question.score)
            self.assertEqual(dateutil.parser.parse(item['last_activity_date']), question.last_activity_date)
            self.assertEqual(dateutil.parser.parse(item['creation_date']), question.creation_date)
            self.assertEqual(dateutil.parser.parse(item['last_edit_date']), question.last_edit_date)
            self.assertEqual(item['content_license'], question.content_license)
            self.assertEqual(item['title'], question.title)
            if item['owner'] is not None:
                self.assertEqual(item['owner']['reputation'], question.owner.reputation)
                self.assertEqual(item['owner']['user_id'], question.owner_id)
                self.assertEqual(item['owner']['display_name'], question.owner.display_name)
                self.assertEqual(item['owner']['user_type'], question.owner.user_type())
