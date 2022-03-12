"""Posts view set testing
"""
import dateutil.parser

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .. import factories
from stackexchange import enums, models


class PostTests(APITestCase):
    """Post view set tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        factories.PostFactory.create_batch(size=1000)

    def test_list(self):
        """Test post list endpoint
        """
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user information returned is correct
        for row in response.json()['items']:
            post = models.Post.objects.get(pk=row['post_id'])
            self.assertEqual(row['score'], post.score)
            self.assertEqual(dateutil.parser.parse(row['last_activity_date']), post.last_activity_date)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), post.creation_date)
            self.assertEqual(row['post_type'], enums.PostType(post.type).name.lower())
            self.assertEqual(row['content_license'], enums.ContentLicense[post.content_license].name)
