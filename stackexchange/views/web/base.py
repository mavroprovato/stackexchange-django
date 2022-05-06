"""Base web view classes
"""
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView


class BaseListView(ListView):
    """The base list view.
    """
    # The page title
    title = None
    # The page heading
    heading = None

    def get_context_data(self, **kwargs) -> dict:
        """Get the context data.

        :param kwargs: The keyword arguments.
        :return: The context data
        """
        context = super().get_context_data(**kwargs)

        return context | {
            'title': self.title,
            'heading': self.heading,
            'page_range': context['paginator'].get_elided_page_range(
                context['page_obj'].number, on_each_side=2, on_ends=1
            )
        }


class BaseDetailView(DetailView):
    """The base detail view.
    """
    # The page title
    title = None
    # The page heading
    heading = None

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Return the detail view. Makes sure that the URL includes the slug.

        :param request: The request.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :return: The response.
        """
        obj = self.get_object()
        if obj.slug() != self.kwargs.get('slug'):
            return redirect(obj)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        """Get the context data.

        :param kwargs: The keyword arguments.
        :return: The context data
        """
        context = super().get_context_data(**kwargs)

        return context | {
            'title': self.title,
            'heading': self.heading
        }
