"""Base web view classes
"""
from django.views.generic import ListView


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
