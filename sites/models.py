"""The application models
"""
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

from sites import managers


class Site(TenantMixin):
    """The site model.
    """
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, help_text="The parent site")
    name = models.CharField(max_length=32, unique=True, help_text="The site name")
    description = models.CharField(max_length=64, help_text="The site description")
    long_description = models.CharField(max_length=128, help_text="The site long description")
    url = models.URLField(help_text="The site URL")
    image_url = models.URLField(help_text="The site image URL")
    icon_url = models.URLField(help_text="The site icon URL")
    badge_icon_url = models.URLField(help_text="The site badge icon URL")
    tag_css = models.TextField(help_text="CSS for tags")
    tagline = models.CharField(max_length=256, help_text="The site tagline")
    total_questions = models.PositiveIntegerField(default=0, help_text="The site total question count")
    total_answers = models.PositiveIntegerField(default=0, help_text="The site total answer count")
    total_users = models.PositiveIntegerField(default=0, help_text="The site total user count")
    total_comments = models.PositiveIntegerField(default=0, help_text="The site total comment count")
    total_tags = models.PositiveIntegerField(default=0, help_text="The site total tag count")
    last_post_date = models.DateTimeField(null=True, blank=True, help_text="The date of the last post")

    class Meta:
        db_table = 'sites'

    def __str__(self) -> str:
        """Return the string representation of the site.

        :return: The site name.
        """
        return str(self.name)


class Domain(DomainMixin):
    """The domain model.
    """
    pass


class User(AbstractBaseUser):
    """The user model.
    """
    USERNAME_FIELD = 'username'

    username = models.CharField(max_length=255, unique=True, help_text="The user name")
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True, help_text="The user email")
    staff = models.BooleanField(default=False, help_text="True if the user is member of the staff")

    objects = managers.UserManager()

    class Meta:
        db_table = 'users'

    def is_staff(self) -> bool:
        """Return True if the user is a staff user.

        :return: True if the user is a staff user.
        """
        return self.staff

    def has_perm(self, *_) -> bool:
        """Return True if the user has the specified permission. Admin users have all permissions.

        :return: True if the user is an admin user.
        """
        return self.is_staff()

    def has_perms(self, perm_list, obj=None) -> bool:
        """Return True if the user has each of the specified permissions. If object is passed, check if the user has all
        required perms for it.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, *_) -> bool:
        """Return True if the user has any permissions in the given app label. Admin users have all permissions.

        :return: True if the user is an admin user.
        """
        return self.is_staff()

    def __str__(self) -> str:
        """Return the string representation of the user.

        :return: The username.
        """
        return str(self.username)

