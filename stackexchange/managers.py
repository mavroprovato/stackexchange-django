"""The managers for the models
"""

from django.contrib.auth.models import UserManager as BaseUserManager


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

        :param username: The user name.
        :param email: The user email.
        :param password: The user password.
        :param extra_fields: The user extra field.
        :return: The created superuser.
        """
        return self._create_user(username, email, password, is_admin=True, **extra_fields)
