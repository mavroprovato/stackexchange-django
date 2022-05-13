"""Web user views
"""
import enum

from django.db.models import QuerySet, OuterRef, Count

from stackexchange import enums, models
from .base import BaseListView, BaseDetailView


class UserViewTab(enum.Enum):
    """The user view tab enumeration
    """
    REPUTATION = '-reputation'
    NEWUSERS = '-creation_date'

    def __init__(self, sort_field: str) -> None:
        """Creates the tag view tab.

        :param sort_field: The sort field.
        """
        self.sort_field = sort_field


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
        tab = UserViewTab[self.request.GET.get('tab', UserViewTab.REPUTATION.name).upper()]

        return models.User.objects.order_by(tab.sort_field)


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
