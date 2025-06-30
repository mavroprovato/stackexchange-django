"""The users factory
"""
import datetime

import factory

from stackexchange import models


class SiteUserFactory(factory.django.DjangoModelFactory):
    """The site user factory
    """
    class Meta:
        model = models.SiteUser

    unique_id = factory.Sequence(lambda x: x)
    display_name = factory.Faker('name')
    website_url = factory.Faker('url')
    location = factory.Faker('city')
    about = factory.Faker('sentence')
    creation_date = factory.Faker('date_time_between', start_date='-1y', tzinfo=datetime.UTC)
    last_access_date = factory.Faker('date_time_between', start_date='-1y', tzinfo=datetime.UTC)
    reputation = factory.Faker('pyint')
    views = factory.Faker('pyint')
    up_votes = factory.Faker('pyint')
    down_votes = factory.Faker('pyint')
