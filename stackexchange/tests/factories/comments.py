"""The comments factory
"""
import datetime

import factory

from stackexchange import enums, models
from .posts import QuestionAnswerFactory
from .site_users import SiteUserFactory


class PostCommentFactory(factory.django.DjangoModelFactory):
    """The post comment factory
    """
    class Meta:
        model = models.PostComment

    post = factory.SubFactory(QuestionAnswerFactory)
    user = factory.SubFactory(SiteUserFactory)
    score = factory.Faker('pyint')
    text = factory.Faker('paragraph')
    creation_date = factory.Faker('date_time_between', start_date='-1y', tzinfo=datetime.UTC)
    content_license = factory.Faker('random_element', elements=[cl.value for cl in enums.ContentLicense])
