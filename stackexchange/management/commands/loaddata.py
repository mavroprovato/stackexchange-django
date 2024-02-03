import datetime
import io
import pathlib
import re
import time
import tempfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db import connection, utils
from django.core.management import call_command
import requests
import py7zr
import tqdm

from stackexchange import services


class Importer:
    """Helper class to import data to the database
    """
    def __init__(self, site: str, output: io.IOBase):
        """Create the importer.

        :param site: The site name.
        :param output: Output stream to write the messages.
        """
        self.site = site
        self.output = output
        self.indexes = self._get_indexes()
        self.temp_dir = None

    def do_import(self):
        """Perform the import.
        """
        self.drop_indexes()
        with tempfile.TemporaryDirectory(dir=settings.TEMP_DIR) as temp_dir:
            self.output.write("Extracting dump")
            with py7zr.SevenZipFile(pathlib.Path(settings.BASE_DIR) / "var" / f"{self.site}.7z", mode='r') as dump_file:
                dump_file.extractall(path=temp_dir)
            self.output.write("Dump extracted")
            self.temp_dir = pathlib.Path(temp_dir)
        self.recreate_indexes()
        self.analyze()
        self.clear_caches()

    @staticmethod
    def _get_indexes() -> dict:
        """Get all database indexes.

        :return: A dictionary with the index name as a key and the index definition as a value.
        """
        output = io.StringIO()
        call_command('sqlmigrate', 'stackexchange', '0001_initial', stdout=output)

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


class Command(BaseCommand):
    """Command to load the data for a stackexchange site.
    """
    help = 'Load the data for a stackexchange site'

    def add_arguments(self, parser: CommandParser):
        """Add the command arguments.

        :param parser: The argument parser.
        """
        parser.add_argument("site", help="The name of the site to download")

    def handle(self, *args, **options):
        """Implements the logic of the command.

        :param args: The arguments.
        :param options: The options.
        """
        site = options['site']
        start = time.time()
        self.stdout.write(f"Loading data for {site}")
        downloader = Downloader(site=site, output=self.stdout)
        downloader.download()
        importer = Importer(site=site, output=self.stdout)
        importer.do_import()
        end = time.time()
        self.stdout.write(f"Data loaded, took {datetime.timedelta(seconds=end-start)}")
