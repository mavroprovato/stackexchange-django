"""Application Celery tasks
"""
import celery

from sites import models
from stackexchange import services


@celery.shared_task
def set_site_info(site: str) -> dict:
    """Calculate the site information from the database.

    :return: The calculated site information.
    """
    site = models.Site.objects.get(name=site)

    return services.site_info.SiteInfo(site=site).calculate()
