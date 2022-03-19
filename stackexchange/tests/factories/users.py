"""The users factory
"""
import factory
import pytz

from stackexchange import models
from .base import BaseModelFactory


class UserFactory(BaseModelFactory):
    """The users factory
    """
    class Meta:
        model = models.User
        django_get_or_create = ('username', )

    username = factory.Faker('user_name')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    display_name = factory.Faker('name')
    website_url = factory.Faker('url')
    location = factory.Faker('city')
    about = factory.Faker('sentence')
    creation_date = factory.Faker('date_time_between', start_date='-1y', tzinfo=pytz.UTC)
    reputation = factory.Faker('pyint')
    views = factory.Faker('pyint')
    up_votes = factory.Faker('pyint')
    down_votes = factory.Faker('pyint')
