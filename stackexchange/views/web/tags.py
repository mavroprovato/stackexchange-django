"""Web tag views
"""
import datetime
import enum

from django.db.models import QuerySet, Subquery, OuterRef, Count

from stackexchange import models
from .base import BaseListView


class TagViewTab(enum.Enum):
    """The tag view tab enumeration
    """
    POPULAR = '-award_count'
    NAME = 'name'

    def __init__(self, sort_field: str) -> None:
        """Creates the tag view tab.

        :param sort_field: The sort field.
        """
        self.sort_field = sort_field


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
        tab = TagViewTab[self.request.GET.get('tab', TagViewTab.POPULAR.name).upper()]
        start_of_day = datetime.datetime.now(datetime.UTC).replace(tzinfo=datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0)
        start_of_week = start_of_day - datetime.timedelta(days=start_of_day.isoweekday())
        start_of_month = start_of_day.replace(day=1)
        start_of_year = start_of_month.replace(month=1)

        return models.Tag.objects.annotate(
            exprert=Subquery(models.Post.objects.filter(pk=OuterRef('excerpt_id')).values('body')[:1]),
            question_count_total=models.Post.objects.filter(
                tags=OuterRef('pk')
            ).values('tags').annotate(count=Count('*')).values('count'),
            question_count_today=models.Post.objects.filter(
                tags=OuterRef('pk'), creation_date__gte=start_of_day
            ).values('tags').annotate(count=Count('*')).values('count'),
            question_count_week=models.Post.objects.filter(
                tags=OuterRef('pk'), creation_date__gte=start_of_week
            ).values('tags').annotate(count=Count('*')).values('count'),
            question_count_month=models.Post.objects.filter(
                tags=OuterRef('pk'), creation_date__gte=start_of_month
            ).values('tags').annotate(count=Count('*')).values('count'),
            question_count_year=models.Post.objects.filter(
                tags=OuterRef('pk'), creation_date__gte=start_of_year
            ).values('tags').annotate(count=Count('*')).values('count')
        ).order_by(tab.sort_field)
