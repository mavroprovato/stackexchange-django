"""Users API comments testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from ..comments.base import BaseCommentTestCase


class UserCommentTests(BaseCommentTestCase):
    """Users view set comments tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
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
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('api-user-comments', kwargs={'pk': user.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the user comments endpoint for multiple users
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.pk) for user in users)}))
        self.assert_items_equal(response)

    def test_sort_by_creation(self):
        """Test the user comment list sorted by comment creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'order': 'asc'}
        )
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'order': 'desc'}
        )
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the user comment list sorted by comment votes.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'order': 'asc'}
        )
        self.assert_sorted(response, 'score')

        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'order': 'desc'}
        )
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_creation(self):
        """Test the user comments list endpoint range by creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'reputation', min_value, max_value)

    def test_range_by_votes(self):
        """Test the user comments list endpoint range by comment score.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = 3000
        max_value = 6000
        response = self.client.get(
            reverse('api-user-comments', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'score', min_value, max_value)
