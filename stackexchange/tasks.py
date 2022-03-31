"""Application Celery tasks
"""
import celery

from stackexchange import services


@celery.shared_task
def set_site_info() -> dict:
    """Calculate the site information from the database.

    :return: The calculated site information.
    """
    return services.set_site_info()
