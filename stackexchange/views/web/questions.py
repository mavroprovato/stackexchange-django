"""Web question views
"""
from django.db.models import QuerySet, Prefetch
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView

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

    def get_context_data(self, **kwargs) -> dict:
        """Get the context data for the view.

        :param kwargs: The keyword arguments.
        :return: The context data.
        """
        context = super().get_context_data(**kwargs)

        return context | {
            'title': "Newest Questions - Stackexchange Django",
            'heading': "All Questions",
            'page_range': context['paginator'].get_elided_page_range(
                context['page_obj'].number, on_each_side=2, on_ends=1
            )
        }


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
