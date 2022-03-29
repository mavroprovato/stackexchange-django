"""Posts view set comment testing
"""
import random

from django.urls import reverse

from stackexchange import models
from stackexchange.tests import factories
from ..comments.base import BaseCommentTestCase


class PostCommentsTests(BaseCommentTestCase):
    """Post view set comments tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=100)
        posts = []
        for user in users:
            for _ in range(3):
                posts.append(factories.QuestionAnswerFactory.create(owner=user))
        for _ in range(1000):
            for _ in range(3):
                factories.CommentFactory.create(post=random.choice(posts), user=random.choice(users))

    def test(self):
        """Test the post comment retrieve endpoint.
        """
        comment = random.sample(list(models.Comment.objects.all()), 1)[0]
        response = self.client.get(reverse('post-comments', kwargs={'pk': comment.pk}))
        self.assert_items_equal(response)

    def test_multiple(self):
        """Test the post comment retrieve endpoint for multiple ids.
        """
        comments = random.sample(list(models.Comment.objects.all()), 3)
        response = self.client.get(
            reverse('post-comments', kwargs={'pk': ';'.join(str(comment.pk) for comment in comments)}))
        self.assert_items_equal(response)
