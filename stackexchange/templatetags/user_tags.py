"""Template tags for user tags
"""
from django import template

from stackexchange import models

register = template.Library()


@register.inclusion_tag('stackexchange/templatetags/comment_user_display.html')
def comment_user_display(comment: models.PostComment) -> dict:
    """Tag for displaying users for comments.

    :param comment: The comment.
    :return: The context for displaying the user for a comment.
    """
    return {
        'user': comment.user,
        'user_display_name': comment.user_display_name
    }
