"""The questions factory
"""
from .posts import PostFactory
from stackexchange import enums


class QuestionFactory(PostFactory):
    """The question factory
    """
    type = enums.PostType.QUESTION.value
