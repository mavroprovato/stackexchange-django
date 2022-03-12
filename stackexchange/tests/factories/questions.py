"""The questions factory
"""
from stackexchange import enums
from .posts import PostFactory


class QuestionFactory(PostFactory):
    """The question factory
    """
    type = enums.PostType.QUESTION.value
