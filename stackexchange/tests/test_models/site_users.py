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
        cls.user = factories.SiteUserFactory.create()

    def test_display_name(self):
        """Test the display name field
        """
        self.assertEqual(self.user._meta.get_field('display_name').verbose_name, 'display name')
        self.assertEqual(self.user._meta.get_field('display_name').help_text, 'The site user display name')
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
        self.assertEqual(self.user._meta.get_field('creation_date').help_text, 'The site user creation date')
        self.assertEqual(self.user._meta.get_field('creation_date').unique, False)
        self.assertEqual(self.user._meta.get_field('creation_date').null, False)

    def test_last_modified_date(self):
        """Test the last modified date field
        """
        self.assertEqual(self.user._meta.get_field('last_modified_date').verbose_name, 'last modified date')
        self.assertEqual(self.user._meta.get_field('last_modified_date').help_text, 'The site user last modified date')
        self.assertEqual(self.user._meta.get_field('last_modified_date').unique, False)
        self.assertEqual(self.user._meta.get_field('last_modified_date').null, False)

    def test_last_access_date(self):
        """Test the last access date field
        """
        self.assertEqual(self.user._meta.get_field('last_access_date').verbose_name, 'last access date')
        self.assertEqual(self.user._meta.get_field('last_access_date').help_text, 'The site user last access date')
        self.assertEqual(self.user._meta.get_field('last_access_date').unique, False)
        self.assertEqual(self.user._meta.get_field('last_access_date').null, False)

    def test_reputation(self):
        """Test the reputation field
        """
        self.assertEqual(self.user._meta.get_field('reputation').verbose_name, 'reputation')
        self.assertEqual(self.user._meta.get_field('reputation').help_text, 'The site user reputation')
        self.assertEqual(self.user._meta.get_field('reputation').unique, False)
        self.assertEqual(self.user._meta.get_field('reputation').null, False)
        self.assertEqual(self.user._meta.get_field('reputation').default, 0)

    def test_views(self):
        """Test the views field
        """
        self.assertEqual(self.user._meta.get_field('views').verbose_name, 'views')
        self.assertEqual(self.user._meta.get_field('views').help_text, 'The site user views')
        self.assertEqual(self.user._meta.get_field('views').unique, False)
        self.assertEqual(self.user._meta.get_field('views').null, False)
        self.assertEqual(self.user._meta.get_field('views').default, 0)

    def test_up_votes(self):
        """Test the up votes field
        """
        self.assertEqual(self.user._meta.get_field('up_votes').verbose_name, 'up votes')
        self.assertEqual(self.user._meta.get_field('up_votes').help_text, 'The site user up votes')
        self.assertEqual(self.user._meta.get_field('up_votes').unique, False)
        self.assertEqual(self.user._meta.get_field('up_votes').null, False)
        self.assertEqual(self.user._meta.get_field('up_votes').default, 0)

    def test_down_votes(self):
        """Test the down votes field
        """
        self.assertEqual(self.user._meta.get_field('down_votes').verbose_name, 'down votes')
        self.assertEqual(self.user._meta.get_field('down_votes').help_text, 'The site user down votes')
        self.assertEqual(self.user._meta.get_field('down_votes').unique, False)
        self.assertEqual(self.user._meta.get_field('down_votes').null, False)
        self.assertEqual(self.user._meta.get_field('down_votes').default, 0)

    def test_str(self):
        """Test the string representation.
        """
        self.assertEqual(str(self.user), self.user.display_name)
