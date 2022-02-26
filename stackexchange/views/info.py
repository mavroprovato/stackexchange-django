"""The info view set
"""
from django.db.models import Count, Max, Min, Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.request import Request
from rest_framework.response import Response

from stackexchange import enums, models, serializers
from stackexchange.views import BaseListViewSet


@extend_schema_view(
    list=extend_schema(summary='Returns a collection of statistics about the site', description=' ')
)
class InfoViewSet(BaseListViewSet):
    """The info view set
    """
    serializer_class = serializers.InfoSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """The list endpoint. Returns statistics about the site.

        :param request: The request.
        :return: The site statistics.
        """
        info = {
            **models.UserBadge.objects.aggregate(
                total_badges=Count('*'), first_badge_date=Min('date_awarded'), last_badge_date=Max('date_awarded')
            ),
            **models.Post.objects.filter(type=enums.PostType.QUESTION).aggregate(
                total_questions=Count('*'), total_accepted=Count('pk', filter=Q(accepted_answer__isnull=False)),
                first_question_date=Min('creation_date'), last_question_date=Max('creation_date')
            ),
            **models.Post.objects.filter(type=enums.PostType.ANSWER).aggregate(
                total_answers=Count('*'), first_answer_date=Min('creation_date'), last_answer_date=Max('creation_date')
            ),
            **{
                "total_users": models.User.objects.count(),
                "total_votes": models.PostVote.objects.count(),
                "total_comments": models.Comment.objects.count(),
            }
        }
        if info.get('total_badges') and info.get('first_badge_date') and info.get('last_badge_date'):
            info['badges_per_minute'] = info['total_badges'] / ((
                    info['last_badge_date'] - info['first_badge_date']
            ).total_seconds() / 60)
        if info.get('total_questions') and info.get('first_question_date') and info.get('last_question_date'):
            info['questions_per_minute'] = info['total_questions'] / ((
                    info['last_question_date'] - info['first_question_date']
            ).total_seconds() / 60)
        if info.get('total_answers') and info.get('first_answer_date') and info.get('last_answer_date'):
            info['answers_per_minute'] = info['total_answers'] / ((
                    info['last_answer_date'] - info['first_answer_date']
            ).total_seconds() / 60)

        queryset = self.paginate_queryset([self.serializer_class(info).data])

        return self.get_paginated_response(queryset)
