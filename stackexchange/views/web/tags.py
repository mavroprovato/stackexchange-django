"""Web tag views
"""
from django.db.models import QuerySet
from django.views.generic import ListView

from stackexchange import models


class TagView(ListView):
    """The question view
    """
    template_name = 'tags.html'
    context_object_name = 'tags'
    paginate_by = 30

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return models.Tag.objects.all()

    def get_context_data(self, **kwargs) -> dict:
        """Get the contest data for the view.

        :param kwargs: The keyword arguments.
        :return: The context data.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'title': "Tags - Stackexchange Django",
            'heading': "Tags"
        })

        return context
