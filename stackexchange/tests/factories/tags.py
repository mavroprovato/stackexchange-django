"""The tags factory
"""
import factory

from stackexchange import models


class TagFactory(factory.django.DjangoModelFactory):
    """The tags factory
    """
    class Meta:
        model = models.Tag
        django_get_or_create = ('name', )

    name = factory.Faker('slug')
    award_count = factory.Faker('pyint')
    moderator_only = factory.Faker('boolean')
    required = factory.Faker('boolean')
