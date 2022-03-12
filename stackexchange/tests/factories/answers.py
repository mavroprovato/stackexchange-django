"""The answers factory
"""
from .posts import PostFactory
from stackexchange import enums


class AnswersFactory(PostFactory):
    """The answers factory
    """
    type = enums.PostType.ANSWER.value
