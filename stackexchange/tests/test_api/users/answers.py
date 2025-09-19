"""Users API answers testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class UserAnswerTests(base.BaseTestCase):
    """Users view set answer tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=100)
        questions = []
        for site_user in site_users:
            questions += factories.QuestionFactory.create_batch(size=2, owner=site_user)
        for question in questions:
            factories.AnswerFactory.create_batch(size=2, question=question, owner=random.choice(site_users))

    def test(self):
        """Test the user answer list endpoint
        """
        site_user = random.sample(list(models.SiteUser.objects.all()), 1)[0]
        response = self.client.get(reverse('api-user-answers', kwargs={'pk': site_user.unique_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)

    def test_multiple(self):
        """Test the user answer endpoint for multiple ids.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-answers', kwargs={'pk': ';'.join(str(site_user.unique_id) for site_user in site_users)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)

    def test_sort_by_activity(self):
        """Test the user answer endpoint sorted by activity date.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse(
                    'api-user-answers', kwargs={'pk': ';'.join(str(site_user.unique_id) for site_user in site_users)}
                ), data={'sort': 'activity', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'last_activity_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_creation(self):
        """Test user answer endpoint sorted by creation date.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse(
                    'api-user-answers', kwargs={'pk': ';'.join(str(site_user.unique_id) for site_user in site_users)}
                ), data={'sort': 'creation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_votes(self):
        """Test the user answer list endpoint sorted by votes.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        for order in enums.OrderingDirection:
            response = self.client.get(
                reverse(
                    'api-user-answers', kwargs={'pk': ';'.join(str(site_user.unique_id) for site_user in site_users)}
                ), data={'sort': 'votes', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_answer_response(response)
            self.assert_items_sorted(response, 'score', order, enums.OrderingFieldType.INTEGER)

    def test_range_by_activity(self):
        """Test the user answer list endpoint range by activity.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-user-answers', kwargs={'pk': ';'.join(str(site_user.unique_id) for site_user in site_users)}),
            data={'sort': 'activity', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'last_activity_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the user answer list endpoint range by creation date.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-user-answers', kwargs={'pk': ';'.join(str(site_user.unique_id) for site_user in site_users)}),
            data={'sort': 'creation', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_votes(self):
        """Test the user answer list endpoint range by votes.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value, max_value = self.generate_random_integers(max_value=3_000)
        response = self.client.get(
            reverse('api-user-answers', kwargs={'pk': ';'.join(str(site_user.unique_id) for site_user in site_users)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'score', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_date_range(self):
        """Test the user answer endpoint by date range.
        """
        from_date, to_date = self.generate_random_date_range()
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-answers', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
            data={'fromdate': from_date.isoformat(), 'todate': to_date.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_answer_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, from_date, to_date)
