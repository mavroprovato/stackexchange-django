"""Throttling configuration module
"""
from django.views import View
from rest_framework.throttling import UserRateThrottle


class Burst(UserRateThrottle):
    """The burst user throttle
    """
    scope = 'burst'


class Sustained(UserRateThrottle):
    """The sustained user throttle
    """
    scope = 'sustained'

    def get_max_quota(self) -> int:
        """Get the maximum quota allowed for the user

        :return: The maximum quota allowed for the user.
        """
        return self.parse_rate(self.get_rate())[0]

    def get_remaining_quota(self, view: View) -> int:
        """Get the remaining quota allowed for the user

        :param view: The view.
        :return: The remaining quota allowed for the user.
        """
        key = self.get_cache_key(view.request, view)
        history = self.cache.get(key, [])

        return self.get_max_quota() - len(history)
