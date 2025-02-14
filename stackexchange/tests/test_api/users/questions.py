"""Users API questions testing
"""
import datetime
import random

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from ..questions.base import BaseQuestionTestCase


class UserQuestionTests(BaseQuestionTestCase):
    """Users view set question tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        site = factories.SiteFactory.create()
        site_users = factories.SiteUserFactory.create_batch(site=site, size=100)
        for site_user in site_users:
            factories.QuestionFactory.create_batch(size=3, owner=site_user)

    def test(self):
        """Test user questions endpoint
        """
        site_user = random.sample(list(models.SiteUser.objects.all()), 1)[0]
        response = self.client.get(reverse('api-user-questions', kwargs={'pk': site_user.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the user questions endpoint for multiple ids.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-questions', kwargs={'pk': ';'.join(str(site_user.pk) for site_user in site_users)}))
        self.assert_items_equal(response)

    def test_sort_by_activity(self):
        """Test the user questions endpoint sorted by activity date.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-questions', kwargs={'pk': ';'.join(str(site_user.pk) for site_user in site_users)}),
            data={'sort': 'activity', 'order': 'asc'}
        )
        self.assert_sorted(response, 'last_activity_date')

        response = self.client.get(
            reverse('api-user-questions', kwargs={'pk': ';'.join(str(site_user.pk) for site_user in site_users)}),
            data={'sort': 'activity', 'order': 'desc'}
        )
        self.assert_sorted(response, 'last_activity_date', reverse=True)

    def test_sort_by_creation_date(self):
        """Test the user questions endpoint sorted by creation date.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-questions', kwargs={'pk': ';'.join(str(site_user.pk) for site_user in site_users)}),
            data={'sort': 'creation', 'order': 'asc'}
        )
        self.assert_sorted(response, 'creation_date')

        response = self.client.get(
            reverse('api-user-questions', kwargs={'pk': ';'.join(str(site_user.pk) for site_user in site_users)}),
            data={'sort': 'creation', 'order': 'desc'}
        )
        self.assert_sorted(response, 'creation_date', reverse=True)

    def test_sort_by_votes(self):
        """Test the user questions endpoint sorted by votes.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        response = self.client.get(
            reverse('api-user-questions', kwargs={'pk': ';'.join(str(site_user.pk) for site_user in site_users)}),
            data={'sort': 'votes', 'order': 'asc'}
        )
        self.assert_sorted(response, 'score')

        response = self.client.get(
            reverse('api-user-questions', kwargs={'pk': ';'.join(str(site_user.pk) for site_user in site_users)}),
            data={'sort': 'votes', 'order': 'desc'}
        )
        self.assert_sorted(response, 'score', reverse=True)

    def test_range_by_activity(self):
        """Test the user questions endpoint range by activity.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-user-questions', kwargs={'pk': ';'.join(str(site_user.pk) for site_user in site_users)}),
            data={'sort': 'activity', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'last_activity_date', min_value, max_value)

    def test_range_by_creation_date(self):
        """Test the user questions endpoint range by user creation date.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value = (datetime.datetime.utcnow() - datetime.timedelta(days=300)).date()
        max_value = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).date()
        response = self.client.get(
            reverse('api-user-questions', kwargs={'pk': ';'.join(str(site_user.pk) for site_user in site_users)}),
            data={'sort': 'creation', 'min': min_value.isoformat(), 'max': max_value.isoformat()}
        )
        self.assert_range(response, 'creation_date', min_value, max_value)

    def test_range_by_votes(self):
        """Test the user questions endpoint range by votes.
        """
        site_users = random.sample(list(models.SiteUser.objects.all()), 3)
        min_value = 3000
        max_value = 6000
        response = self.client.get(
            reverse('api-user-questions', kwargs={'pk': ';'.join(str(site_user.pk) for site_user in site_users)}),
            data={'sort': 'votes', 'min': min_value, 'max': max_value}
        )
        self.assert_range(response, 'score', min_value, max_value)
