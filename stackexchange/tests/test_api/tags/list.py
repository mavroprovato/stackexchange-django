"""Tag view set list testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import models
from stackexchange.tests import factories


class TagListTests(APITestCase):
    """Tag view set list tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.TagFactory.create_batch(size=10)

    def test(self):
        """Test tag list endpoint
        """
        # Test that the list endpoint returns successfully
        response = self.client.get(reverse('tag-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the tag information returned is correct
        for row in response.json()['items']:
            tag = models.Tag.objects.get(name=row['name'])
            self.assertEqual(row['count'], tag.award_count)
