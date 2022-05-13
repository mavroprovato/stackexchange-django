"""Web user views
"""
from django.db.models import QuerySet, OuterRef, Count

from stackexchange import enums, models
from .base import BaseListView, BaseDetailView


class UserView(BaseListView):
    """The user view
    """
    paginate_by = 36
    title = "Users"
    heading = "Users"

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return models.User.objects.order_by('-reputation')


class UserDetailView(BaseDetailView):
    """The user detail view.
    """
    model = models.User

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return super().get_queryset().annotate(
            answer_count=models.Post.objects.filter(
                owner=OuterRef('pk'), type=enums.PostType.ANSWER
            ).values('owner').annotate(count=Count('pk')).values('count'),
            question_count=models.Post.objects.filter(
                owner=OuterRef('pk'), type=enums.PostType.QUESTION
            ).values('owner').annotate(count=Count('pk')).values('count'),
        )

    @property
    def title(self) -> str:
        """Return the page title.

        :return: The user display name.
        """
        return self.object.display_name

    @property
    def heading(self) -> str:
        """Return the page heading.

        :return: The user display name.
        """
        return self.object.display_name
