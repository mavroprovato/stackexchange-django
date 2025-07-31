"""Posts view set revisions testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import enums, models
from stackexchange.tests import base, factories


class PostRevisionsTests(base.BaseTestCase):
    """Post view set revisions tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        site_users = factories.SiteUserFactory.create_batch(size=100)
        posts = []
        for site_user in site_users:
            posts += factories.PostFactory.create_batch(size=3, owner=site_user)
        for post in posts:
            factories.PostHistoryFactory.create_batch(size=3, post=post)

    def test(self):
        """Test the post revisions endpoint
        """
        post = random.sample(list(models.Post.objects.all()), 1)[0]
        response = self.client.get(reverse('api-post-revisions', kwargs={'pk': post.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_post_revision_response(response)

    def test_multiple(self):
        """Test the post revisions endpoint for multiple ids.
        """
        posts = random.sample(
            list(models.Post.objects.filter(type__in=(enums.PostType.QUESTION, enums.PostType.ANSWER))), 3)
        response = self.client.get(
            reverse('api-post-revisions', kwargs={'pk': ';'.join(str(post.pk) for post in posts)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_post_revision_response(response)
