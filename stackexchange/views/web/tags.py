"""Web tag views
"""
from django.db.models import QuerySet, Subquery, OuterRef, Count

from stackexchange import models
from .base import BaseListView


class TagView(BaseListView):
    """The tag view
    """
    paginate_by = 36
    title = "Tags"
    heading = "Tags"

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view.

        :return: The queryset for the view.
        """
        return models.Tag.objects.annotate(
            exprert=Subquery(models.Post.objects.filter(pk=OuterRef('excerpt_id')).values('body')[:1]),
            question_count=models.Post.objects.filter(tags=OuterRef('pk')).values('tags').annotate(
                question_count=Count('*')
            ).values('question_count')
        ).order_by('-award_count')
