"""The comments factory
"""
import factory

from stackexchange import models
from .posts import QuestionAnswerFactory
from .users import UserFactory


class CommentFactory(factory.django.DjangoModelFactory):
    """The comments factory
    """
    class Meta:
        model = models.Comment

    post = factory.SubFactory(QuestionAnswerFactory)
    score = factory.Faker('pyint')
    text = factory.Faker('paragraph')
    user = factory.SubFactory(UserFactory)
