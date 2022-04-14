"""Web question views
"""
from django.views.generic import TemplateView


class QuestionView(TemplateView):
    """The index view
    """
    template_name = 'questions.html'
