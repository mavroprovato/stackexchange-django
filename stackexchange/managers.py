"""The managers for the models
"""

from django.apps import apps
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db.models import Manager, OuterRef, Count, Subquery, QuerySet
from django.db.models.functions import Coalesce

from stackexchange import enums


class UserManager(BaseUserManager):
    """The user manager
    """
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create a user.

        :param username: The user name.
        :param email: The user email.
        :param password: The user password.
        :param extra_fields: The user extra field.
        :return: The created user.
        """
        return super().create_user(username, email, password, is_admin=False, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create a superuser.

        :param username: The username.
        :param email: The user email.
        :param password: The user password.
        :param extra_fields: The user extra field.
        :return: The created superuser.
        """
        return self._create_user(username, email, password, is_admin=True, **extra_fields)

    def with_badge_counts(self) -> QuerySet:
        """Annotate the queryset with the badge counts per badge type. Tree fields are added, named
        `<badge_class>_count`.

        :return: The annotated queryset.
        """
        return self.annotate(**{
            f"{badge_class.name.lower()}_count": Coalesce(Subquery(
                apps.get_model('stackexchange', 'UserBadge').objects.filter(
                    user=OuterRef('pk'), badge__badge_class=badge_class.value
                ).values('badge__badge_class').annotate(
                    count=Count('pk')
                ).values('count')
            ), 0)
            for badge_class in enums.BadgeClass
        })


class BadgeQuerySet(QuerySet):
    """The badge queryset
    """
    def with_award_count(self) -> QuerySet:
        """Annotate the queryset with the badge award count. A field named `award_count` is added to the queryset.

        :return: The annotated queryset.
        """
        return self.annotate(
            award_count=Subquery(
                apps.get_model('stackexchange', 'UserBadge').objects.filter(
                    badge=OuterRef('pk')
                ).values('badge').annotate(count=Count('pk')).values('count')
            )
        )
