"""Posts view set retrieve testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import enums, models
from stackexchange.tests import factories
from .base import BasePostTestCase


class PostRetrieveTests(BasePostTestCase):
    """Post view set retrieve tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        site_users = factories.SiteUserFactory.create_batch(size=100)
        for site_user in site_users:
            factories.QuestionAnswerFactory.create(owner=site_user)

    def test(self):
        """Test the post detail endpoint
        """
        post = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 1)[0]
        response = self.client.get(reverse('api-post-detail', kwargs={'pk': post.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the post detail endpoint for multiple ids.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        response = self.client.get(reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}))
        self.assert_items_equal(response)

    def test_sort_by_activity(self):
        """Test the post detail endpoint sorted by activity date.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'activity', 'order': 'asc'}
        )
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'activity', 'order': 'desc'}
        )
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the post detail endpoint sorted by creation date.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'creation', 'order': 'asc'}
        )
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'creation', 'order': 'desc'}
        )
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the post detail endpoint sorted by votes.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'votes', 'order': 'asc'}
        )
        self.assert_sorted(response, 'score')

        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'votes', 'order': 'desc'}
        )
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the post detail endpoint range by activity.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'activity', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the post detail endpoint range by user creation date.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the post detail endpoint range by votes.
        """
        posts = random.sample(list(models.Post.objects.all()), 3)
        min_value = 3000
        max_value = 6000
        response = self.client.get(
            reverse('api-post-detail', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'score', min_value, max_value)
