"""User model tests
"""
from django.test import TestCase
from django.utils import timezone

from stackexchange import models
from stackexchange.tests import factories


class UserModelTests(TestCase):
    """User model tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        cls.user = factories.UserFactory.create()

    def test_username(self):
        """Test the username field
        """
        self.assertEqual(self.user._meta.get_field('username').verbose_name, 'username')
        self.assertEqual(self.user._meta.get_field('username').help_text, 'The user name')
        self.assertEqual(self.user._meta.get_field('username').max_length, 255)
        self.assertEqual(self.user._meta.get_field('username').unique, True)
        self.assertEqual(self.user._meta.get_field('username').null, False)

    def test_email(self):
        """Test the email field
        """
        self.assertEqual(self.user._meta.get_field('email').verbose_name, 'email')
        self.assertEqual(self.user._meta.get_field('email').help_text, 'The user email')
        self.assertEqual(self.user._meta.get_field('email').max_length, 255)
        self.assertEqual(self.user._meta.get_field('email').unique, True)
        self.assertEqual(self.user._meta.get_field('email').null, False)

    def test_display_name(self):
        """Test the display name field
        """
        self.assertEqual(self.user._meta.get_field('display_name').verbose_name, 'display name')
        self.assertEqual(self.user._meta.get_field('display_name').help_text, 'The user display name')
        self.assertEqual(self.user._meta.get_field('display_name').max_length, 255)
        self.assertEqual(self.user._meta.get_field('display_name').unique, False)
        self.assertEqual(self.user._meta.get_field('display_name').null, False)

    def test_website_url(self):
        """Test the website url field
        """
        self.assertEqual(self.user._meta.get_field('website_url').verbose_name, 'website url')
        self.assertEqual(self.user._meta.get_field('website_url').help_text, 'The user web site URL')
        self.assertEqual(self.user._meta.get_field('website_url').unique, False)
        self.assertEqual(self.user._meta.get_field('website_url').null, True)

    def test_location(self):
        """Test the location field
        """
        self.assertEqual(self.user._meta.get_field('location').verbose_name, 'location')
        self.assertEqual(self.user._meta.get_field('location').help_text, 'The user location')
        self.assertEqual(self.user._meta.get_field('location').max_length, 255)
        self.assertEqual(self.user._meta.get_field('location').unique, False)
        self.assertEqual(self.user._meta.get_field('location').null, True)

    def test_creation_date(self):
        """Test the creation date field
        """
        self.assertEqual(self.user._meta.get_field('creation_date').verbose_name, 'creation date')
        self.assertEqual(self.user._meta.get_field('creation_date').help_text, 'The user creation date')
        self.assertEqual(self.user._meta.get_field('creation_date').unique, False)
        self.assertEqual(self.user._meta.get_field('creation_date').null, False)
        self.assertEqual(self.user._meta.get_field('creation_date').default, timezone.now)

    def test_last_modified_date(self):
        """Test the last modified date field
        """
        self.assertEqual(self.user._meta.get_field('last_modified_date').verbose_name, 'last modified date')
        self.assertEqual(self.user._meta.get_field('last_modified_date').help_text, 'The user last modified date')
        self.assertEqual(self.user._meta.get_field('last_modified_date').unique, False)
        self.assertEqual(self.user._meta.get_field('last_modified_date').null, True)

    def test_last_access_date(self):
        """Test the last access date field
        """
        self.assertEqual(self.user._meta.get_field('last_access_date').verbose_name, 'last access date')
        self.assertEqual(self.user._meta.get_field('last_access_date').help_text, 'The user last access date')
        self.assertEqual(self.user._meta.get_field('last_access_date').unique, False)
        self.assertEqual(self.user._meta.get_field('last_access_date').null, True)

    def test_reputation(self):
        """Test the reputation field
        """
        self.assertEqual(self.user._meta.get_field('reputation').verbose_name, 'reputation')
        self.assertEqual(self.user._meta.get_field('reputation').help_text, 'The user reputation')
        self.assertEqual(self.user._meta.get_field('reputation').unique, False)
        self.assertEqual(self.user._meta.get_field('reputation').null, False)
        self.assertEqual(self.user._meta.get_field('reputation').default, 0)

    def test_views(self):
        """Test the views field
        """
        self.assertEqual(self.user._meta.get_field('views').verbose_name, 'views')
        self.assertEqual(self.user._meta.get_field('views').help_text, 'The user profile views')
        self.assertEqual(self.user._meta.get_field('views').unique, False)
        self.assertEqual(self.user._meta.get_field('views').null, False)
        self.assertEqual(self.user._meta.get_field('views').default, 0)

    def test_up_votes(self):
        """Test the up votes field
        """
        self.assertEqual(self.user._meta.get_field('up_votes').verbose_name, 'up votes')
        self.assertEqual(self.user._meta.get_field('up_votes').help_text, 'The user up votes')
        self.assertEqual(self.user._meta.get_field('up_votes').unique, False)
        self.assertEqual(self.user._meta.get_field('up_votes').null, False)
        self.assertEqual(self.user._meta.get_field('up_votes').default, 0)

    def test_down_votes(self):
        """Test the down votes field
        """
        self.assertEqual(self.user._meta.get_field('down_votes').verbose_name, 'down votes')
        self.assertEqual(self.user._meta.get_field('down_votes').help_text, 'The user down votes')
        self.assertEqual(self.user._meta.get_field('down_votes').unique, False)
        self.assertEqual(self.user._meta.get_field('down_votes').null, False)
        self.assertEqual(self.user._meta.get_field('down_votes').default, 0)

    def test_is_active(self):
        """Test the is active field
        """
        self.assertEqual(self.user._meta.get_field('is_active').verbose_name, 'is active')
        self.assertEqual(self.user._meta.get_field('is_active').help_text, 'True if the user is active')
        self.assertEqual(self.user._meta.get_field('is_active').unique, False)
        self.assertEqual(self.user._meta.get_field('is_active').null, False)
        self.assertEqual(self.user._meta.get_field('is_active').default, True)

    def test_is_moderator(self):
        """Test the is moderator field
        """
        self.assertEqual(self.user._meta.get_field('is_moderator').verbose_name, 'is moderator')
        self.assertEqual(self.user._meta.get_field('is_moderator').help_text, 'True if the user is a moderator')
        self.assertEqual(self.user._meta.get_field('is_moderator').unique, False)
        self.assertEqual(self.user._meta.get_field('is_moderator').null, False)
        self.assertEqual(self.user._meta.get_field('is_moderator').default, False)

    def test_is_employee(self):
        """Test the is employee field
        """
        self.assertEqual(self.user._meta.get_field('is_employee').verbose_name, 'is employee')
        self.assertEqual(self.user._meta.get_field('is_employee').help_text, 'True if the user is an employee')
        self.assertEqual(self.user._meta.get_field('is_employee').unique, False)
        self.assertEqual(self.user._meta.get_field('is_employee').null, False)
        self.assertEqual(self.user._meta.get_field('is_employee').default, False)

    def test_str(self):
        """Test the string representation.
        """
        self.assertEqual(str(self.user), self.user.display_name)

    def test_is_staff(self):
        """Test the is staff property.
        """
        self.assertEqual(self.user.is_staff, self.user.is_employee)

    def test_is_superuser(self):
        """Test the is superuser property.
        """
        self.assertEqual(self.user.is_superuser, self.user.is_employee)

    def test_manager_create_user(self):
        """Test the create user manager method.
        """
        user = models.User.objects.create_user(username='test', email='test@example.com')
        self.assertEqual(user.username, 'test')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.is_employee, False)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

    def test_manager_create_superuser(self):
        """Test the create superuser manager method.
        """
        user = models.User.objects.create_superuser(username='test', email='test@example.com')
        self.assertEqual(user.username, 'test')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.is_employee, True)
        # self.assertEqual(user.is_staff, True)
        self.assertEqual(user.is_superuser, True)
