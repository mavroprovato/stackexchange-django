"""Users API comments testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class UserCommentTests(base.BaseTestCase):
    """Users view set comments tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=10)
        posts = []
        for site_user in site_users:
            for _ in range(3):
                posts.append(factories.QuestionAnswerFactory.create(owner=site_user))
        for _ in range(100):
            for _ in range(3):
                factories.PostCommentFactory.create(post=random.choice(posts), user=random.choice(site_users))

    def test(self):
        """Test the user comments endpoint
        """
        user = random.sample(list(models.SiteUser.objects.all()), 1)[0]
        response = self.client.get(reverse('api-user-comments', kwargs={'pk': user.unique_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)

    def test_multiple(self):
        """Test the user comments endpoint for multiple users
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)

    def test_sort_by_creation(self):
        """Test the user comment endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            users = random.sample(list(models.SiteUser.objects.all()), 3)
            response = self.client.get(
                reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
                data={'sort': 'creation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_comment_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_votes(self):
        """Test the user comment endpoint sorted by votes.
        """
        for order in enums.OrderingDirection:
            users = random.sample(list(models.SiteUser.objects.all()), 3)
            response = self.client.get(
                reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
                data={'sort': 'votes', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_comment_response(response)
            self.assert_items_sorted(response, 'score', order, enums.OrderingFieldType.INTEGER)

    def test_range_by_creation(self):
        """Test the user comment endpoint range by creation date.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_votes(self):
        """Test the user comment endpoint range by votes.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value, max_value = self.generate_random_integers()
        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)
        self.assert_items_in_range(response, 'score', enums.OrderingFieldType.INTEGER, min_value, max_value)

    def test_date_range(self):
        """Test the user comment endpoint date range.
        """
        users = random.sample(list(models.SiteUser.objects.all()), 3)
        from_date, to_date = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.unique_id) for user in users)}), data={
                'fromdate': from_date.isoformat(), 'todate': to_date.isoformat()
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_comment_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, from_date, to_date)
