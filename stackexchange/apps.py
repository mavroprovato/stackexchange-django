"""Stackexchange app definition
"""
from django.apps import AppConfig


class StackExchangeConfig(AppConfig):
    """The stackexchange application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stackexchange'
