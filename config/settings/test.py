"""Settings for tests
"""
from .default import *

# Disable throttling for test
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = ()
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}
