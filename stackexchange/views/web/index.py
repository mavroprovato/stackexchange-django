"""Web index views
"""
from django.views.generic import TemplateView


class IndexView(TemplateView):
    """The index view
    """
    template_name = "index.html"
