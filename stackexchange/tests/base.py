"""Base test case
"""
import datetime
import random
import uuid

import dateutil.parser
from django.db.models import QuerySet, Exists, OuterRef
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
            self.assertEqual(answer.type, enums.PostType.ANSWER)
            self.assertEqual(item['score'], answer.score)
            self.assertEqual(dateutil.parser.parse(item['last_activity_date']), answer.last_activity_date)
            self.assertEqual(dateutil.parser.parse(item['creation_date']), answer.creation_date)
            self.assertEqual(item['question_id'], answer.question_id)
            self.assertEqual(item['content_license'], answer.content_license)
            self.assert_user(item, 'owner', answer.owner)

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
            self.assert_user(item, 'user', site_user)

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
            self.assert_user(item, 'owner', comment.user)

    def assert_question_response(self, response, no_answers=False, unanswered=False):
        """Assert that the question response schema is correct.

        :param no_answers: True if that there are no answers for this question should be tested.
        :param unanswered: True if that question is unanswered should be tested.
        :param response: The response.
        """
        for item in response.json()['items']:
            question = models.Post.objects.get(id=item['question_id'])
            self.assertEqual(question.type, enums.PostType.QUESTION)
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
            self.assert_user(item, 'owner', question.owner)
            self.assert_tags(item, question.tags)
            if no_answers:
                self.assertTrue(question.answer_count == 0)
            if unanswered:
                self.assertTrue(models.Post.objects.filter(~Exists(
                    models.Post.objects.filter(question=OuterRef('pk'), type=enums.PostType.ANSWER, score__gt=0)
                )))

    def assert_post_response(self, response):
        """Assert that the post response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            post = models.Post.objects.get(id=item['post_id'])
            self.assertEqual(item['score'], post.score)
            self.assertEqual(dateutil.parser.parse(item['last_activity_date']), post.last_activity_date)
            self.assertEqual(dateutil.parser.parse(item['creation_date']), post.creation_date)
            self.assertEqual(item['post_type'], post.type)
            self.assertEqual(item['post_id'], post.id)
            self.assertEqual(item['content_license'], post.content_license)
            self.assert_user(item, 'owner', post.owner)

    def assert_post_revision_response(self, response):
        """Assert that the post revision response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            # This is not 100% correct, as many post history objects can exist with the same post id and revision
            post_history = models.PostHistory.objects.get(
                post_id=item['post_id'], revision_guid=item['revision_guid']
            )
            self.assertEqual(item['set_community_wiki'], post_history.type == enums.PostHistoryType.COMMUNITY_OWNED)
            self.assertEqual(item['is_rollback'], enums.PostHistoryType(post_history.type).rollback())
            self.assertEqual(dateutil.parser.parse(item['creation_date']), post_history.creation_date)
            self.assertEqual(item['post_id'], post_history.post.id)
            self.assertEqual(item['post_type'], post_history.post.type)
            # Need to check for revision number here
            self.assertEqual(item['revision_type'],
                             'vote_based' if enums.PostHistoryType(post_history.type).vote_based() else 'single_user')
            self.assertEqual(item['comment'], post_history.comment)
            self.assertEqual(uuid.UUID(item['revision_guid']), post_history.revision_guid)
            self.assert_user(item, 'owner', post_history.user)

    def assert_tag_response(self, response):
        """Assert that the tag response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            tag = models.Tag.objects.get(name=item['name'])
            self.assertEqual(item['is_required'], tag.required)
            self.assertEqual(item['is_moderator_only'], tag.moderator_only)
            self.assertEqual(item['count'], tag.award_count)
            self.assertEqual(item['name'], tag.name)

    def assert_tag_wiki_response(self, response):
        """Assert that the tag wiki response schema is correct.

        :param response: The response.
        """
        for item in response.json()['items']:
            tag = models.Tag.objects.get(name=item['tag_name'])
            self.assertEqual(dateutil.parser.parse(item['excerpt_last_edit_date']), tag.excerpt.last_edit_date)
            self.assertEqual(dateutil.parser.parse(item['body_last_edit_date']), tag.wiki.last_edit_date)
            self.assertEqual(item['excerpt'], tag.excerpt.body)
            self.assertEqual(item['tag_name'], tag.name)

    def assert_user(self, item: dict, user_attr: str, user: models.SiteUser):
        """Assert that the user response schema is correct.

        :param item: The response item.
        :param user_attr: The user attribute name.
        :param user: The user.
        """
        if item[user_attr] is not None:
            self.assertEqual(item[user_attr]['reputation'], user.reputation)
            self.assertEqual(item[user_attr]['user_id'], user.id)
            self.assertEqual(item[user_attr]['display_name'], user.display_name)
            self.assertEqual(item[user_attr]['user_type'], user.user_type())

    def assert_tags(self, item: dict, tags: QuerySet):
        """Assert that the tags are correct.

        :param item: The response item.
        :param tags: The tags.
        """
        self.assertCountEqual(item['tags'], (tag.name for tag in tags.all()))

    @staticmethod
    def generate_random_integers(min_value: int = 0, max_value: int = 3_000) -> tuple[int, int]:
        """Generate a random integer range between two values.

        :param min_value: The minimum value.
        :param max_value: The maximum value.
        :return: A tuple of the start and end dates.
        """
        val1 = random.randrange(min_value, max_value)
        val2 = random.randrange(min_value, max_value)

        return (val1, val2) if val1 < val2 else (val2, val1)

    @staticmethod
    def generate_random_date_range() -> tuple[datetime.date, datetime.date]:
        """Generate a random date range for the last year.

        :return: A tuple of the start and end dates.
        """
        start_days, end_days = sorted(random.sample(range(365), 2), reverse=True)

        return (
            datetime.date.today() - datetime.timedelta(days=start_days),
            datetime.date.today() - datetime.timedelta(days=end_days)
        )
