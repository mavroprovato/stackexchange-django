"""The post votes factory
"""
import factory

from stackexchange import enums, models
from .posts import QuestionFactory
from .users import SiteUserFactory


class PostVoteFactory(factory.django.DjangoModelFactory):
    """The post votes factory
    """
    class Meta:
        model = models.PostVote

    post = factory.SubFactory(QuestionFactory)
    type = factory.Faker('random_element', elements=[pvt.value for pvt in enums.PostVoteType])
    user = factory.SubFactory(SiteUserFactory)
    bounty_amount = factory.Faker('pyint')
