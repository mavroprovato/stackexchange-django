"""Badges view set recipients detail testing
"""
import random

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from .base import BaseBadgeTestCase


class BadgeRecipientDetailTests(BaseBadgeTestCase):
    """Badges view set recipient detail tests
    """
    @classmethod
    def setUpTestData(cls):
        users = factories.UserFactory.create_batch(size=10)
        badges = factories.BadgeFactory.create_batch(size=25)
        for _ in range(1000):
            factories.UserBadgeFactory.create(user=random.choice(users), badge=random.choice(badges))

    def test(self):
        """Test badges recipients endpoint
        """
        badge = random.sample(list(models.Badge.objects.all()), 1)[0]
        response = self.client.get(reverse('badge-recipients-detail', kwargs={'pk': badge.pk}))
        self.assert_items_equal(response)
