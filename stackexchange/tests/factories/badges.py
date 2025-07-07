"""The badges factory
"""
import datetime

import factory

from stackexchange import enums, models
from .site_users import SiteUserFactory


class BadgeFactory(factory.django.DjangoModelFactory):
    """The badges factory
    """
    class Meta:
        model = models.Badge
        django_get_or_create = ('name', )

    name = factory.Faker('word')
    rank = factory.Faker('random_element', elements=[bc.value for bc in enums.BadgeRank])
    badge_type = factory.Faker('random_element', elements=[bt.value for bt in enums.BadgeType])


class UserBadgeFactory(factory.django.DjangoModelFactory):
    """The user badge factory
    """
    class Meta:
        model = models.UserBadge

    user = factory.SubFactory(SiteUserFactory)
    badge = factory.SubFactory(BadgeFactory)
    date_awarded = factory.Faker('date_time_between', start_date='-1y', tzinfo=datetime.UTC)
