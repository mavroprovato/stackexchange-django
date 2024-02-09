"""The sites factory
"""
import factory

from stackexchange import models


class SiteFactory(factory.django.DjangoModelFactory):
    """The sites factory
    """
    class Meta:
        model = models.Site
        django_get_or_create = ('name', )

    name = factory.Faker('name')
