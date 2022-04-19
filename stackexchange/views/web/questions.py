"""Web question views
"""
from django.db.models import QuerySet
from django.views.generic import ListView, DetailView

from stackexchange import enums, models


class QuestionView(ListView):
    """The question view
    """
    template_name = 'questions.html'
    context_object_name = 'questions'
    paginate_by = 30

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return models.Post.objects.filter(type=enums.PostType.QUESTION).select_related('owner').prefetch_related(
            'tags').order_by('-creation_date')

    def get_context_data(self, **kwargs) -> dict:
        """Get the context data for the view.

        :param kwargs: The keyword arguments.
        :return: The context data.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'title': "Newest Questions - Stackexchange Django",
            'heading': "All Questions"
        })

        return context


class QuestionTaggedView(QuestionView):
    """The question tagged view
    """
    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return super().get_queryset().filter(tags__name=self.kwargs['tag'])

    def get_context_data(self, **kwargs) -> dict:
        """Get the context data for the view.

        :param kwargs: The keyword arguments.
        :return: The context data.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f"Newest '{self.kwargs['tag']}' Questions - Stackexchange Django",
            'heading': f"Questions tagged [{self.kwargs['tag']}]",
        })

        return context


class QuestionDetailView(DetailView):
    """The question detail view.
    """
    model = models.Post
    template_name = 'question_detail.html'
    context_object_name = 'question'

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return super().get_queryset().prefetch_related('answers', 'comments__user')

    def get_context_data(self, **kwargs) -> dict:
        """Get the context data for the view.

        :param kwargs: The keyword arguments.
        :return: The context data.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f"{self.object.title} - Stackexchange Django",
        })

        return context
