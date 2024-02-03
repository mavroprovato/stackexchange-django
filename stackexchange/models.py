"""The application models
"""
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class Site(models.Model):
    """The site model
    """
    name = models.CharField(max_length=255, unique=True, help_text="The site name")

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
