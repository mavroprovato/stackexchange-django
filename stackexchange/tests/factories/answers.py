"""The answers factory
"""
from stackexchange import enums
from .posts import PostFactory


class AnswerFactory(PostFactory):
    """The answer factory
    """
    type = enums.PostType.ANSWER.value
