"""Class for loading site data.
"""
import logging
import pathlib
import re
import tempfile

from django.conf import settings
import py7zr

from stackexchange import models
from . import dowloader, xmlparser

# The module logger
logger = logging.getLogger(__name__)


class SiteDataLoader:
    """Helper class to load site data
    """
    def __init__(self, site: str):
        """Create the importer.

        :param site: The site name.
        """
        self.site_id = models.Site.objects.get(name=site)

        downloader = dowloader.Downloader(
            filename=f"{models.Site.objects.get(name=site).url.replace('https://', '')}.7z")
        self.site_data_file = downloader.get_file()

    def load(self):
        """Perform the import.
        """
        with tempfile.TemporaryDirectory(dir=settings.TEMP_DIR) as temp_dir:
            logger.info("Extracting data file %s", self.site_data_file)
            with py7zr.SevenZipFile(self.site_data_file, mode='r') as dump_file:
                dump_file.extractall(path=temp_dir)
            logger.info("Data file extracted")
            self._load_users(pathlib.Path(temp_dir) / 'Users.xml')

    def _load_users(self, file: pathlib.Path):
        logger.info("Loading users")
        for row in xmlparser.XmlFileIterator(xml_file=file):
            print(row.keys())

    @staticmethod
    def _get_indexes() -> dict:
        """Get all database indexes.

        :return: A dictionary with the index name as a key and the index definition as a value.
        """
        call_command('sqlmigrate', 'stackexchange', '0001_initial')

        return {
            re.search(r'"(.*?)"', line).group(1): line
            for line in output.getvalue().splitlines() if line.startswith("CREATE INDEX")
        }

    def drop_indexes(self):
        """Drop indexes from the database.
        """
        self.output.write("Dropping indexes")
        with connection.cursor() as cursor:
            for index_name in self.indexes.keys():
                try:
                    cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
                except utils.InternalError:
                    pass
        self.output.write("Indexes dropped")

    def recreate_indexes(self):
        """Recreate the indexes from the database.
        """
        self.output.write("Creating indexes")
        with connection.cursor() as cursor:
            for index_name, index_definition in self.indexes.items():
                try:
                    cursor.execute(index_definition)
                except utils.ProgrammingError:
                    pass
        self.output.write("Indexes created")

    def analyze(self):
        """Analyze the tables.
        """
        self.output.write("Analyzing")
        with connection.cursor() as cursor:
            cursor.execute("ANALYZE")
        self.output.write("Analyze completed")

    def clear_caches(self):
        """Clear the caches
        """
        self.output.write("Clearing caches")
        services.clear_cache()
        self.output.write("Caches cleared")
