"""Class for loading site data.
"""
import csv
import logging
import pathlib
import tempfile

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import connection
import py7zr

from stackexchange import models
from . import dowloader, siteinfo, xmlparser

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
        downloader = dowloader.Downloader(filename=f"{site.url.replace('https://', '')}.7z")
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

            user_loader = UserLoader(site_id=self.site_id, data_dir=pathlib.Path(temp_dir))
            user_loader.load()

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


class UserLoader:
    """The user loader
    """
    def __init__(self, site_id: int, data_dir: pathlib.Path):
        """Create the user loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory.
        """
        self.site_id = site_id
        self.data_dir = data_dir
        self.existing_users = set(models.User.objects.values_list('pk', flat=True))

    def load(self):
        """Load the users.
        """
        logger.info("Loading user data")
        with (
            (self.data_dir / 'users.csv').open('wt') as users_file,
            (self.data_dir / 'site_users.csv').open('wt') as site_users_file
        ):
            users_writer = csv.writer(users_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            site_users_writer = csv.writer(site_users_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Users.xml'):
                user_id = None
                if 'AccountId' in row:
                    user_id = int(row['AccountId'])
                    if user_id not in self.existing_users:
                        users_writer.writerow([
                            user_id, 'admin' if user_id == -1 else f"user{row['AccountId']}",
                            make_password('admin') if user_id == -1 else '', '<NULL>', user_id == -1
                        ])
                        self.existing_users.add(user_id)

                site_users_writer.writerow([
                    self.site_id, row['Id'], '<NULL>' if user_id is None else user_id, row['DisplayName'],
                    row.get('WebsiteUrl', '<NULL>'), row.get('Location', '<NULL>'), row.get('AboutMe', '<NULL>'),
                    row['CreationDate'], row['LastAccessDate'], row['Reputation'], row['Views'], row['UpVotes'],
                    row['DownVotes']
                ])

        logger.info("Loading users")
        with connection.cursor() as cursor:
            with (self.data_dir / 'users.csv').open('rt') as users_file:
                cursor.copy_from(
                    users_file, table='users', columns=('id', 'username', 'password', 'email', 'staff'),
                    sep=',', null='<NULL>')

        logger.info("Loading site users")
        models.SiteUser.objects.filter(site_id=self.site_id).delete()
        with connection.cursor() as cursor:
            with (self.data_dir / 'site_users.csv').open('rt') as site_users_file:
                cursor.copy_from(
                    site_users_file, table='site_users', columns=(
                        'site_id', 'site_user_id', 'user_id', 'display_name', 'website_url', 'location', 'about',
                        'creation_date', 'last_access_date', 'reputation', 'views', 'up_votes', 'down_votes'
                    ), sep=',', null='<NULL>')
