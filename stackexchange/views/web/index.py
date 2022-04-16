"""Web index views
"""
from django.views.generic import RedirectView


class IndexView(RedirectView):
    """The index view
    """
    pattern_name = 'web-questions'
