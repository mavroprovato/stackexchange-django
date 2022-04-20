"""The posts factory
"""
import factory
import pytz

from stackexchange import enums, models
from .tags import TagFactory
from .users import UserFactory


class PostFactory(factory.django.DjangoModelFactory):
    """The posts factory
    """
    class Meta:
        model = models.Post

    title = factory.Faker('sentence')
    body = factory.Faker('paragraph')
    type = factory.Faker('random_element', elements=[pt.value for pt in enums.PostType])
    creation_date = factory.Faker('date_time_between', start_date='-1y', tzinfo=pytz.UTC)
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


class QuestionFactory(PostFactory):
    """The question factory
    """
    type = enums.PostType.QUESTION.value


class AnswerFactory(PostFactory):
    """The answer factory
    """
    type = enums.PostType.ANSWER.value
    question = factory.SubFactory(QuestionFactory)


class QuestionTagFactory(factory.django.DjangoModelFactory):
    """The question tag factory
    """
    class Meta:
        model = models.PostTag
        django_get_or_create = ('post', 'tag')

    post = factory.SubFactory(QuestionFactory)
    tag = factory.SubFactory(TagFactory)


class PostHistoryFactory(factory.django.DjangoModelFactory):
    """The post history factory
    """
    class Meta:
        model = models.PostHistory

    type = factory.Faker('random_element', elements=[pt.value for pt in enums.PostHistoryType])
    post = factory.SubFactory(PostFactory)
    revision_guid = factory.Faker('uuid4')
    creation_date = factory.Faker('date_time_between', start_date='-1y', tzinfo=pytz.UTC)
    user = factory.SubFactory(UserFactory)
    user_display_name = factory.Faker('user_name')
    comment = factory.Faker('sentence')
    text = factory.Faker('sentence')
