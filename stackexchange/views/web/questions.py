"""Web question views
"""
from django.db.models import QuerySet
from django.views.generic import ListView

from stackexchange import enums, models


class QuestionView(ListView):
    """The question view
    """
    template_name = 'questions.html'
    paginate_by = 30

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return models.Post.objects.filter(type=enums.PostType.QUESTION).select_related('owner').prefetch_related(
            'tags').order_by('-creation_date')


class QuestionTaggedView(QuestionView):
    """The question tagged view
    """
    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return super().get_queryset().filter(tags__name=self.kwargs['tag'])
