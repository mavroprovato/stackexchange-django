"""The answers factory
"""
from stackexchange import enums
from .posts import PostFactory


class AnswersFactory(PostFactory):
    """The answers factory
    """
    type = enums.PostType.ANSWER.value
