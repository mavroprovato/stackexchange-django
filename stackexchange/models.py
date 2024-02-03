"""The application models
"""
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class Site(models.Model):
    """The site model
    """
    name = models.CharField(max_length=32, unique=True, help_text="The site name")
    description = models.CharField(max_length=64, unique=True, help_text="The site description")
    long_description = models.CharField(max_length=128, unique=True, help_text="The site long description")
    url = models.URLField(help_text="The site URL")
    image_url = models.URLField(help_text="The site image URL")
    icon_url = models.URLField(help_text="The site icon URL")
    badge_icon_url = models.URLField(help_text="The site badge icon URL")
    tag_css = models.TextField(help_text="CSS for tags")
    tagline = models.CharField(max_length=256, help_text="The site tagline")
    total_questions = models.PositiveIntegerField(help_text="The site total question count")
    total_answers = models.PositiveIntegerField(help_text="The site total answer count")
    total_users = models.PositiveIntegerField(help_text="The site total user count")
    total_comments = models.PositiveIntegerField(help_text="The site total comment count")
    total_tags = models.PositiveIntegerField(help_text="The site total tag count")
    last_post = models.DateTimeField(help_text="The date of the last post")

    class Meta:
        db_table = 'sites'

    def __str__(self) -> str:
        """Return the string representation of the site.

        :return: The site name.
        """
        return str(self.name)


class User(AbstractBaseUser):
    """The user model
    """
    USERNAME_FIELD = 'username'

    username = models.CharField(help_text="The user name", max_length=255, unique=True)
    display_name = models.CharField(help_text="The user display name", max_length=255)
    website_url = models.URLField(help_text="The user web site URL", null=True, blank=True)
    location = models.CharField(help_text="The user location", max_length=255, null=True, blank=True)
    about = models.TextField(help_text="The user about information", null=True, blank=True)

    class Meta:
        db_table = 'users'

    def is_staff(self) -> bool:
        """Return True if the user is a staff user.

        :return: True if the user is a staff user.
        """
        return False
