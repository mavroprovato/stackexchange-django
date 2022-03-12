"""The badges factory
"""
import factory

from stackexchange import enums, models


class BadgeFactory(factory.django.DjangoModelFactory):
    """The badges factory
    """
    class Meta:
        model = models.Badge
        django_get_or_create = ('name', )

    name = factory.Faker('word')
    badge_class = factory.Faker('random_element', elements=[bc.value for bc in enums.BadgeClass])
    badge_type = factory.Faker('random_element', elements=[bt.value for bt in enums.BadgeType])
