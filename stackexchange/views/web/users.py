"""Web user views
"""
from django.db.models import QuerySet, Subquery, OuterRef, Count
from django.views.generic import ListView

from stackexchange import models


class UserView(ListView):
    """The user view
    """
    template_name = 'users.html'
    context_object_name = 'users'
    paginate_by = 36

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return models.User.objects.order_by('-reputation')

    def get_context_data(self, **kwargs) -> dict:
        """Get the context data for the view.

        :param kwargs: The keyword arguments.
        :return: The context data.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'title': "Users - Stackexchange Django",
            'heading': "Users"
        })

        return context
