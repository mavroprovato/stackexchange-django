"""Settings for tests
"""
from .settings import *

# Disable throttling for test
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = ()
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}
