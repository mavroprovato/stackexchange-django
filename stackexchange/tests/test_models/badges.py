"""Badge model tests
"""
from django.test import TestCase

from stackexchange.tests import factories


class BadgeModelTests(TestCase):
    """Badge model tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        cls.badge = factories.BadgeFactory.create()

    def test_name(self):
        """Test the name field
        """
        self.assertEqual(self.badge._meta.get_field('name').verbose_name, 'name')
        self.assertEqual(self.badge._meta.get_field('name').help_text, 'The badge name')
        self.assertEqual(self.badge._meta.get_field('name').max_length, 255)
        self.assertEqual(self.badge._meta.get_field('name').unique, True)
        self.assertEqual(self.badge._meta.get_field('name').null, False)

    def test_class(self):
        """Test the badge class field
        """
        self.assertEqual(self.badge._meta.get_field('badge_class').verbose_name, 'badge class')
        self.assertEqual(self.badge._meta.get_field('badge_class').help_text, 'The badge class')
        self.assertEqual(self.badge._meta.get_field('badge_class').null, False)

    def test_type(self):
        """Test the badge type field
        """
        self.assertEqual(self.badge._meta.get_field('badge_type').verbose_name, 'badge type')
        self.assertEqual(self.badge._meta.get_field('badge_type').help_text, 'The badge type')
        self.assertEqual(self.badge._meta.get_field('badge_type').null, False)

    def test_str(self):
        """Test the string representation.
        """
        self.assertEqual(str(self.badge), self.badge.name)
