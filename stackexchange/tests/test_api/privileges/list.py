"""Privileges view set testing
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums


class PrivilegesTests(APITestCase):
    """Privileges view set tests
    """
    def test(self):
        """Test privileges list endpoint
        """
        response = self.client.get(reverse('api-privilege-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for privilege_item in response.json()['items']:
            privilege = enums.Privilege[privilege_item['short_description'].upper().replace(' ', '_')]
            self.assertEqual(privilege.reputation, privilege_item['reputation'])
            self.assertEqual(privilege.description, privilege_item['description'])
