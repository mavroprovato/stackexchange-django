"""The users factory
"""
import factory

from stackexchange import models


class UserFactory(factory.django.DjangoModelFactory):
    """The users factory
    """
    class Meta:
        model = models.User
        django_get_or_create = ('username', )

    username = factory.Faker('user_name')
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)
    display_name = factory.Faker('name')
    website_url = factory.Faker('url')
    location = factory.Faker('city')
    about = factory.Faker('sentence')
    reputation = factory.Faker('pyint')
    views = factory.Faker('pyint')
    up_votes = factory.Faker('pyint')
    down_votes = factory.Faker('pyint')
