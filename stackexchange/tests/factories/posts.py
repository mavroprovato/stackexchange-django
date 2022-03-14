"""The posts factory
"""
import factory
import pytz

from .users import UserFactory
from stackexchange import enums, models


class PostFactory(factory.django.DjangoModelFactory):
    """The posts factory
    """
    class Meta:
        model = models.Post

    title = factory.Faker('sentence')
    body = factory.Faker('paragraph')
    type = factory.Faker('random_element', elements=[pt.value for pt in enums.PostType])
    last_activity_date = factory.Faker('date_time_between', start_date='-1y', tzinfo=pytz.UTC)
    score = factory.Faker('pyint')
    view_count = factory.Faker('pyint')
    answer_count = factory.Faker('pyint')
    comment_count = factory.Faker('pyint')
    favorite_count = factory.Faker('pyint')
    owner = factory.SubFactory(UserFactory)


class QuestionAnswerFactory(PostFactory):
    """The question or answer factory
    """
    type = factory.Faker('random_element', elements=(enums.PostType.QUESTION.value, enums.PostType.ANSWER.value))
