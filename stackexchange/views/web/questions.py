"""Web question views
"""
from django.db.models import QuerySet, Prefetch

from stackexchange import enums, models
from .base import BaseListView, BaseDetailView


class QuestionView(BaseListView):
    """The question view
    """
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


class QuestionDetailView(BaseDetailView):
    """The question detail view.
    """
    model = models.Post

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return super().get_queryset().prefetch_related(
            'tags',
            Prefetch('comments__user', queryset=models.Comment.objects.order_by('creation_date')),
            Prefetch('answers', queryset=models.Post.objects.order_by('-score')),
            Prefetch('answers__comments__user', queryset=models.Comment.objects.order_by('creation_date')),
        )

    @property
    def title(self) -> str:
        """Return the page title.

        :return: The post title.
        """
        return self.object.title

    @property
    def heading(self) -> str:
        """Return the page heading.

        :return: The post title.
        """
        return self.object.title
