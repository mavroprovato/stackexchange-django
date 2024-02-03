"""Services module
"""
import logging

from django.core.cache import cache
from django.db.models import Count, Max, Min, Q

from stackexchange import enums, models

logger = logging.getLogger(__name__)


def get_site_info() -> dict:
    """Get the site information.

    :return: The site information, as a dictionary.
    """
    return cache.get_or_set(key='site_info', default=_calculate_site_info, timeout=None)


def set_site_info() -> dict:
    """Set the site information, overriding any cache values.

    :return: The site information, as a dictionary.
    """
    site_info = _calculate_site_info()
    cache.set(key='site_info', value=site_info, timeout=None)

    return site_info


def clear_cache():
    """Clear the site info cache.
    """
    cache.delete(key='site_info')


def _calculate_site_info() -> dict:
    """Calculate the site information.

    :return: The site information.
    """
    logger.info('Calculating site info')
    site_info = {
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
            'total_users': models.User.objects.count(),
            'total_votes': models.PostVote.objects.count(),
            'total_comments': models.Comment.objects.count(),
        }
    }
    if site_info.get('total_badges') and site_info.get('first_badge_date') and site_info.get('last_badge_date'):
        site_info['badges_per_minute'] = site_info['total_badges'] / (
                (site_info['last_badge_date'] - site_info['first_badge_date']).total_seconds() / 60
        )
    if (
            site_info.get('total_questions') and site_info.get('first_question_date') and
            site_info.get('last_question_date')
    ):
        site_info['questions_per_minute'] = site_info['total_questions'] / (
                (site_info['last_question_date'] - site_info['first_question_date']).total_seconds() / 60
        )
    if site_info.get('total_answers') and site_info.get('first_answer_date') and site_info.get('last_answer_date'):
        site_info['answers_per_minute'] = site_info['total_answers'] / (
                (site_info['last_answer_date'] - site_info['first_answer_date']).total_seconds() / 60
        )

    return site_info
