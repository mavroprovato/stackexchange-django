"""Class for loading site data.
"""
import logging
import tempfile

from django.conf import settings
from django.db import connection
import py7zr

from stackexchange import models
from . import dowloader, siteinfo

# The module logger
logger = logging.getLogger(__name__)


class SiteDataLoader:
    """Helper class to load site data
    """
    def __init__(self, site: str):
        """Create the importer.

        :param site: The site name.
        """
        site = models.Site.objects.get(name=site)
        self.site_id = site.id
        # Get the latest file
        downloader = dowloader.Downloader(filename=f"{site.name}.7z")
        self.site_data_file = downloader.get_file()

    def load(self):
        """Load the site data.
        """
        # Extract the data from the archive
        with tempfile.TemporaryDirectory(dir=settings.TEMP_DIR) as temp_dir:
            logger.info("Extracting data file %s", self.site_data_file)
            with py7zr.SevenZipFile(self.site_data_file, mode='r') as dump_file:
                dump_file.extractall(path=temp_dir)
            logger.info("Data file extracted")

        # Post load actions
        self.analyze()
        siteinfo.clear_cache()

    @staticmethod
    def analyze():
        """Analyze the tables.
        """
        logger.info("Analyzing the database")
        with connection.cursor() as cursor:
            cursor.execute("ANALYZE")
        logger.info("Analyze completed")
