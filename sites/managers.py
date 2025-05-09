"""The managers for the models
"""
from django.contrib.auth.models import UserManager as BaseUserManager


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

