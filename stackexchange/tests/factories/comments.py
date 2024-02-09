"""The comments factory
"""
import factory

from stackexchange import models
from .posts import QuestionAnswerFactory
from .users import UserFactory


class PostCommentFactory(factory.django.DjangoModelFactory):
    """The post comment factory
    """
    class Meta:
        model = models.PostComment

    post = factory.SubFactory(QuestionAnswerFactory)
    score = factory.Faker('pyint')
    text = factory.Faker('paragraph')
    user = factory.SubFactory(UserFactory)
