"""Throttling configuration module
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BurstAnon(AnonRateThrottle):
    """The burst anonymous user throttle
    """
    scope = 'burst'


class BurstUser(UserRateThrottle):
    """The burst authenticated user throttle
    """
    scope = 'burst'


class SustainedAnon(AnonRateThrottle):
    """The sustained anonymous user throttle
    """
    scope = 'sustained'


class SustainedUser(UserRateThrottle):
    """The sustained authenticated user throttle
    """
    scope = 'sustained'
