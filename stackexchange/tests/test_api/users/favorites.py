"""Users API comments testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import enums, models
from stackexchange.tests import factories
from ..questions.base import BaseQuestionTestCase


class UserFavoriteTests(BaseQuestionTestCase):
    """Users view set favorite tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        site = factories.SiteFactory.create()
        site_users = factories.SiteUserFactory.create_batch(site=site, size=10)
        questions = []
        for site_user in site_users:
            questions += factories.QuestionFactory.create_batch(size=3, owner=site_user)
        for _ in range(1000):
            factories.PostVoteFactory(
                post=random.choice(questions), type=enums.PostVoteType.FAVORITE.value, user=random.choice(site_users))

    def test(self):
        """Test the user favorites endpoint
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('api-user-favorites', kwargs={'pk': user.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the user favorites endpoint for multiple users
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-favorites', kwargs={'pk': ';'.join(str(user.pk) for user in users)}))
        self.assert_items_equal(response)

    def test_sort_by_activity(self):
        """Test the user favorites endpoint sorted by activity date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-favorites', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'activity', 'order': 'asc'}
        )
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(
            reverse('api-user-favorites', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'activity', 'order': 'desc'}
        )
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation(self):
        """Test the user favorites endpoint sorted by comment creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-favorites', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'order': 'asc'}
        )
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(
            reverse('api-user-favorites', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'order': 'desc'}
        )
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the user favorites endpoint sorted by comment votes.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-favorites', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'order': 'asc'}
        )
        self.assert_sorted(response, 'score')

        response = self.client.get(
            reverse('api-user-favorites', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'order': 'desc'}
        )
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the user favorites endpoint range by activity.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-user-favorites', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'activity', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation(self):
        """Test the user favorites endpoint range by creation date.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-user-favorites', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'creation', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'reputation', min_value, max_value)

    def test_range_by_votes(self):
        """Test the user favorites endpoint range by comment score.
        """
        users = random.sample(list(models.User.objects.all()), 3)
        min_value = 3000
        max_value = 6000
        response = self.client.get(
            reverse('api-user-favorites', kwargs={'pk': ';'.join(str(user.pk) for user in users)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'score', min_value, max_value)
