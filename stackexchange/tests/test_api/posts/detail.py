"""Posts view set retrieve testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class PostRetrieveTests(base.BaseTestCase):
    """Post view set retrieve tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=100)
        for site_user in site_users:
            factories.QuestionAnswerFactory.create(owner=site_user)

    def test(self):
        """Test the post detail endpoint
        """
        post = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 1)[0]
        response = self.client.get(reverse('api-post-detail', kwargs={'pk': post.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_post_response(response)

    def test_multiple(self):
        """Test the post detail endpoint for multiple ids.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_post_response(response)

    def test_sort_by_activity(self):
        """Test the post detail endpoint sorted by activity date.
        """
        for order in enums.OrderingDirection:
            posts = random.sample(
                list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
            response = self.client.get(
                reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
                data={'sort': 'activity', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_post_response(response)
            self.assert_items_sorted(response, 'last_activity_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_creation_date(self):
        """Test the post detail endpoint sorted by creation date.
        """
        for order in enums.OrderingDirection:
            posts = random.sample(
                list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
            response = self.client.get(
                reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
                data={'sort': 'creation', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_post_response(response)
            self.assert_items_sorted(response, 'creation_date', order, enums.OrderingFieldType.DATE)

    def test_sort_by_votes(self):
        """Test the post detail endpoint sorted by votes.
        """
        for order in enums.OrderingDirection:
            posts = random.sample(
                list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
            response = self.client.get(
                reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
                data={'sort': 'votes', 'order': order.value}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_post_response(response)
            self.assert_items_sorted(response, 'score', order, enums.OrderingFieldType.INTEGER)

    def test_range_by_activity(self):
        """Test the post detail endpoint range by activity.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'activity', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_post_response(response)
        self.assert_items_in_range(response, 'last_activity_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the post detail endpoint range by user creation date.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        min_value, max_value = self.generate_random_date_range()
        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_post_response(response)
        self.assert_items_in_range(response, 'creation_date', enums.OrderingFieldType.DATE, min_value, max_value)

    def test_range_by_votes(self):
        """Test the post detail endpoint range by votes.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        min_value, max_value = self.generate_random_integers()
        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_post_response(response)
        self.assert_items_in_range(response, 'score', enums.OrderingFieldType.INTEGER, min_value, max_value)
