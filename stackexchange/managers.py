"""The managers for the models
"""
import collections.abc

from django.apps import apps
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import connection
from django.db.models import OuterRef, Count, Subquery, QuerySet, Min
from django.db.models.functions import Coalesce

from stackexchange import enums


class UserManager(BaseUserManager):
    """The user manager
    """
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create a user.

        :param username: The username.
        :param email: The user email.
        :param password: The user password.
        :param extra_fields: The user extra field.
        :return: The created user.
        """
        if 'display_name' not in extra_fields:
            extra_fields['display_name'] = username

        return super()._create_user(username, email, password, staff=False, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create a superuser.

        :param username: The username.
        :param email: The user email.
        :param password: The user password.
        :param extra_fields: The user extra field.
        :return: The created superuser.
        """
        if 'display_name' not in extra_fields:
            extra_fields['display_name'] = username

        return self._create_user(username, email, password, staff=True, **extra_fields)


class BadgeQuerySet(QuerySet):
    """The badge queryset
    """
    def with_award_count(self) -> QuerySet:
        """Annotate the queryset with the badge award count. A field named `award_count` is added to the queryset.

        :return: The annotated queryset.
        """
        return self.annotate(
            award_count=Coalesce(Subquery(
                apps.get_model('stackexchange', 'UserBadge').objects.filter(
                    badge=OuterRef('pk')
                ).values('badge').annotate(count=Count('pk')).values('count')
            ), 0)
        )


class UserBadgeQuerySet(QuerySet):
    """The user badge queryset
    """
    def per_user_and_badge(self) -> dict:
        """Returns a distinct queryset per user and badge. The queryset is annotated with the award count and the first
        date that the badge was awarded to the user.

        :return: The aggregated queryset.
        """
        return self.values(
            'user', 'badge', 'badge__badge_class', 'badge__name', 'badge__badge_type'
        ).annotate(award_count=Count('*'), date_awarded=Min('date_awarded'))


class PostHistoryQuerySet(QuerySet):
    """The post history queryset
    """
    @staticmethod
    def group_by_revision(post_ids: collections.abc.Iterable[str]) -> collections.abc.Iterable[dict]:
        """Group a list of post history objects by revision.

        :param post_ids: The post identifiers.
        :return: The list of revisions.
        """
        sql = '''
            WITH base_query AS (
                SELECT ph.post_id,
                       ph.revision_guid,
                       MIN(ph.creation_date) AS creation_date,
                       ARRAY_AGG(ph.type) AS post_history_types
                  FROM post_history ph
                 WHERE ph.post_id IN %s
                 GROUP BY ph.post_id, ph.revision_guid
            )
            SELECT bq.post_id,
                   bq.revision_guid,
                   bq.creation_date,
                   bq.post_history_types,
                   (
                       SELECT ph.user_id
                       FROM post_history ph
                       WHERE ph.revision_guid = bq.revision_guid
                       LIMIT 1
                   ) AS user_id,
                   (
                       SELECT ph.user_display_name
                       FROM post_history ph
                       WHERE ph.revision_guid = bq.revision_guid
                       LIMIT 1
                   ) AS user_display_name,
                   (
                       SELECT p.type
                       FROM posts p
                       WHERE p.id = bq.post_id
                       LIMIT 1
                   ) AS post_type,
                   (
                       SELECT ph.comment
                       FROM post_history ph
                       WHERE ph.revision_guid = bq.revision_guid
                       LIMIT 1
                   ) AS comment,
                   rank() OVER (PARTITION BY post_id, post_history_types && %s ORDER BY creation_date) revision_number
            FROM base_query bq
            ORDER BY bq.creation_date DESC
        '''
        with connection.cursor() as cursor:
            cursor.execute(sql, (
                tuple(post_ids),
                '{' + ','.join(str(pht.value) for pht in enums.PostHistoryType if pht.vote_based()) + '}'
            ))
            columns = [col[0] for col in cursor.description]

            return [dict(zip(columns, row)) for row in cursor.fetchall()]
