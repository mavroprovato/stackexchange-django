from django.db.models import Count, Max, Min, Q

from stackexchange import enums, models


def get_site_info() -> dict:
    """Get the site information.

    :return: The site information, as a dictionary.
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
        info['badges_per_minute'] = info['total_badges'] / (
            (info['last_badge_date'] - info['first_badge_date']).total_seconds() / 60
        )
    if info.get('total_questions') and info.get('first_question_date') and info.get('last_question_date'):
        info['questions_per_minute'] = info['total_questions'] / (
            (info['last_question_date'] - info['first_question_date']).total_seconds() / 60
        )
    if info.get('total_answers') and info.get('first_answer_date') and info.get('last_answer_date'):
        info['answers_per_minute'] = info['total_answers'] / (
            (info['last_answer_date'] - info['first_answer_date']).total_seconds() / 60
        )

    return info
