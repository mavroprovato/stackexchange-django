"""The tag synonyms factory
"""
import datetime

import factory

from stackexchange import models


class TagSynonymFactory(factory.django.DjangoModelFactory):
    """The tag synonyms factory
    """
    class Meta:
        model = models.TagSynonym
        django_get_or_create = ('from_tag', 'to_tag')

    from_tag = factory.Faker('slug')
    to_tag = factory.Faker('slug')
    creation_date = factory.Faker('date_time_between', start_date='-1y', tzinfo=datetime.UTC)
    last_applied_date = factory.Faker('date_time_between', start_date='-1y', tzinfo=datetime.UTC)
    applied_count = factory.Faker('pyint', min_value=0, max_value=10_000)
