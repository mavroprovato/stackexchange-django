"""Web user views
"""
from django.db.models import QuerySet

from stackexchange import models
from .base import BaseListView


class UserView(BaseListView):
    """The user view
    """
    template_name = 'users.html'
    paginate_by = 36
    title = "Users"
    heading = "Users"

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return models.User.objects.order_by('-reputation')
