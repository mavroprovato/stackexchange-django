"""Module containing custom application exceptions
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError as DRFValidationError


def application_exception_handler(ex: Exception, context: dict):
    """Custom application exception handler

    :param ex: The exception.
    :param context: The context.
    :return: The response.
    """
    response = exception_handler(ex, context)

    if response is not None:
        if isinstance(ex, ValidationError):
            response.data = {
              "error_id": response.status_code,
              "error_message": ex.detail,
              "error_name": 'bad_parameter'
            }
        elif isinstance(ex, DRFValidationError):
            response.data = {
                "error_id": response.status_code,
                "error_message": next(iter(ex.detail)),
                "error_name": 'bad_parameter'
            }

    return response


class ValidationError(DRFValidationError):
    """Application validation error
    """
    def __init__(self, detail: str) -> None:
        """Create the validation error.

        :param detail: The error detail.
        """
        self.detail = detail
