"""User model tests
"""
from django.test import TestCase

from stackexchange.tests import factories


class SiteUserModelTests(TestCase):
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
        self.assertEqual(self.user._meta.get_field('username').blank, False)

    def test_email(self):
        """Test the email field
        """
        self.assertEqual(self.user._meta.get_field('email').verbose_name, 'email')
        self.assertEqual(self.user._meta.get_field('email').help_text, 'The user email')
        self.assertEqual(self.user._meta.get_field('email').max_length, 255)
        self.assertEqual(self.user._meta.get_field('email').unique, True)
        self.assertEqual(self.user._meta.get_field('email').null, True)
        self.assertEqual(self.user._meta.get_field('email').blank, True)

    def test_staff(self):
        """Test the staff field
        """
        self.assertEqual(self.user._meta.get_field('staff').verbose_name, 'staff')
        self.assertEqual(self.user._meta.get_field('staff').help_text, 'True if the user is member of the staff')
        self.assertEqual(self.user._meta.get_field('staff').null, False)
        self.assertEqual(self.user._meta.get_field('staff').blank, False)

    def test_str(self):
        """Test the string representation.
        """
        self.assertEqual(str(self.user), self.user.username)
