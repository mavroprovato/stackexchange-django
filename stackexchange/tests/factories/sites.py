"""The sites factory
"""
import factory

from sites import models


class SiteFactory(factory.django.DjangoModelFactory):
    """The sites factory
    """
    class Meta:
        model = models.Site
        django_get_or_create = ('name', )

    name = factory.Faker('name')
