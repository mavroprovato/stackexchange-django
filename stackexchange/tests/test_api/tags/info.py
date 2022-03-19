"""Tag view set info testing
"""
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import models
from stackexchange.tests import factories


class TagInfoTests(APITestCase):
    """Tag view set info tests
    """
    @classmethod
    def setUpTestData(cls):
        factories.TagFactory.create_batch(size=10)

    def test(self):
        """Test the tag detail endpoint.
        """
        # Test getting one tag
        tag = random.sample(list(models.Tag.objects.all()), 1)[0]
        response = self.client.get(reverse('tag-info', kwargs={'pk': tag.name}))
        self.assertEqual(response.json()['items'][0]['name'], tag.name)

    def test_multiple(self):
        """Test the tag detail endpoint for multiple ids.
        """
        # Test getting multiple tags
        tags = random.sample(list(models.Tag.objects.all()), 3)
        response = self.client.get(reverse('tag-info', kwargs={
            'pk': ';'.join(str(tag.name) for tag in tags)
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual({row['name'] for row in response.json()['items']}, {tag.name for tag in tags})
