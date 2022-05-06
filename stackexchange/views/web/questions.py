"""Web question views
"""
from django.db.models import QuerySet, Prefetch
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView

from stackexchange import enums, models
from .base import BaseListView


class QuestionView(BaseListView):
    """The question view
    """
    template_name = 'questions.html'
    paginate_by = 30
    title = "Newest Questions"
    heading = "All Questions"

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

    @property
    def title(self) -> str:
        """Return the page title.

        :return: The page title.
        """
        return f"Newest '{self.kwargs['tag']}' Questions"

    @property
    def heading(self) -> str:
        """Return the page heading.

        :return: The page heading.
        """
        return f"Questions tagged [{self.kwargs['tag']}]"


class QuestionDetailView(DetailView):
    """The question detail view.
    """
    model = models.Post
    template_name = 'question_detail.html'
    context_object_name = 'question'

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Return the question detail view. Makes sure that the URL

        :param request: The request.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :return: The response.
        """
        obj = self.get_object()
        if obj.slug() != self.kwargs.get('slug'):
            return redirect(obj)

        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return super().get_queryset().prefetch_related(
            Prefetch('answers', queryset=models.Post.objects.order_by('-score')),
            Prefetch('comments__user', queryset=models.Comment.objects.order_by('creation_date')),
            Prefetch('answers__comments__user', queryset=models.Comment.objects.order_by('creation_date')),
        )

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
