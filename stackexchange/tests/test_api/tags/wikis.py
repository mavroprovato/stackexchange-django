"""Tag view set wikis testing
"""
import random

from django.urls import reverse
from rest_framework import status

from stackexchange import models, enums
from stackexchange.tests import base, factories


class TagWikisTests(base.BaseTestCase):
    """Tag view set wikis tests
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test data.
        """
        base.BaseTestCase.setUpClass()
        tags = factories.TagFactory.create_batch(size=10)
        for tag in tags:
            tag.wiki = factories.PostFactory.create(type=enums.PostType.TAG_WIKI)
            tag.excerpt = factories.PostFactory.create(type=enums.PostType.TAG_WIKI_EXPERT)
            tag.save()

    def test(self):
        """Test the tag wikis endpoint.
        """
        tag = random.sample(list(models.Tag.objects.all()), 1)[0]
        response = self.client.get(reverse('api-tag-wikis', kwargs={'pk': tag.name}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_wiki_response(response)

    def test_multiple(self):
        """Test the tag wikis endpoint for multiple ids.
        """
        tags = random.sample(list(models.Tag.objects.all()), 3)
        response = self.client.get(reverse('api-tag-wikis', kwargs={
            'pk': ';'.join(str(tag.name) for tag in tags)
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_tag_wiki_response(response)
