"""Base test case
"""
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient


class BaseTestCase(TenantTestCase):
    """Base test case
    """
    def setUp(self):
        self.client = TenantClient(self.tenant)
