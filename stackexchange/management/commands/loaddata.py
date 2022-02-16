import csv
import datetime
import io
import pathlib
import re
import time
import tempfile
import typing
import xml.etree.ElementTree as eT

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandParser
from django.db import connection, utils
from django.core.management import call_command
import requests
import py7zr
import tqdm


class Downloader:
    """Helper class to download stack exchange site data.
    """
    def __init__(self, site: str, output: io.IOBase):
        """Create the site downloader.

        :param site: The site to download.
        """
        self.site = site
        self.output = output
        self._download_dir = pathlib.Path(settings.BASE_DIR) / "var"
        self._download_dir.mkdir(parents=True, exist_ok=True)

    @property
    def download_url(self) -> str:
        """Get the dump file download URL.

        :return: The dump file download URL.
        """
        return f"https://archive.org/download/stackexchange/{self.site}.7z"

    @property
    def dump_file(self) -> pathlib.Path:
        """Get the local dump file.

        :return: The local dump file.
        """
        return self._download_dir / f"{self.site}.7z"

    @property
    def cache_file(self) -> pathlib.Path:
        """Get the local cache file.

        :return: The local cache file.
        """
        return self._download_dir / f"{self.site}.7z.cache"

    def download(self) -> bool:
        """Download the dump file if needed.

        :return: True if the file was downloaded, False otherwise.
        """
        if self.should_download():
            self.output.write("Downloading dump file")
            # Download file
            with requests.get(self.download_url, stream=True) as response:
                response.raise_for_status()
                total = int(response.headers.get('content-length', 0))
                with open(self.dump_file, 'wb') as f, tqdm.tqdm(
                        desc=self.site, total=total, unit='iB', unit_scale=True
                ) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        size = f.write(data)
                        bar.update(size)
            # Save cache version
            with open(self.cache_file, 'wt') as f:
                f.write(response.headers['ETag'])

            return True

        return False

    def should_download(self) -> bool:
        """Check if the dump file should be downloaded.

        :return: True if the dump file should be downloaded, false otherwise.
        """
        if not self.dump_file.exists():
            self.output.write("Local dump file does not exist")
            return True
        if not self.cache_file.exists():
            self.output.write("Cache file does not exist")
            return True
        if self.dump_changed():
            self.output.write("Dump File has changed")
            return True

        return False

    def dump_changed(self) -> bool:
        """Check if the dump file has changed.

        :return: True if the dump file has changed, False otherwise.
        """
        local_etag = self.cache_file.read_text()
        remote_etag = requests.head(self.download_url, allow_redirects=True).headers['Etag']

        return local_etag != remote_etag


class Importer:
    """Helper class to import data to the database
    """
    USERS_FILE = "Users.xml"
    BADGES_FILE = "Badges.xml"
    POSTS_FILE = "Posts.xml"
    COMMENTS_FILE = "Comments.xml"
    POST_HISTORY_FILE = "PostHistory.xml"
    POST_LINKS_FILE = "PostLinks.xml"
    VOTES_FILE = "Votes.xml"
    TAGS_FILE = "Tags.xml"

    def __init__(self, dump_file: pathlib.Path, output: io.IOBase):
        """Create the imported

        :param dump_file: The dump file to import.
        :param output: Output stream to write the messages.
        """
        self.dump_file = dump_file
        self.output = output
        self.indexes = self._get_indexes()
        self.temp_dir = None

    def do_import(self):
        """Perform the import.
        """
        self.drop_indexes()
        with tempfile.TemporaryDirectory(dir=settings.TEMP_DIR) as temp_dir:
            self.output.write("Extracting dump")
            with py7zr.SevenZipFile(self.dump_file, mode='r') as dump_file:
                dump_file.extractall(path=temp_dir)
            self.output.write("Dump extracted")
            self.temp_dir = pathlib.Path(temp_dir)
            self.load_users()
            self.load_badges()
            self.load_user_badges()
            self.load_posts()
            self.load_comments()
            self.load_post_history()
            self.load_post_links()
            self.load_post_votes()
            self.load_tags()
        self.recreate_indexes()
        self.analyze()

    @staticmethod
    def _get_indexes() -> dict:
        """Get all database indexes.

        :return: A dictionary with the index name as a key and the index definition as a value.
        """
        output = io.StringIO()
        call_command('sqlmigrate', 'stackexchange',  '0001_initial', stdout=output)

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
        """Vacuum full and analyze the tables.
        """
        self.output.write("Analyzing")
        with connection.cursor() as cursor:
            cursor.execute("ANALYZE")
        self.output.write("Analyze completed")

    def load_users(self):
        """Load the users.
        """
        self.output.write(f"Loading users")
        password = make_password("password")
        with (self.temp_dir / 'users.csv').open('wt') as f:
            csv_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in self.iterate_xml(self.temp_dir / self.USERS_FILE):
                csv_writer.writerow([
                    row['Id'], 'admin' if row['Id'] == '-1' else f"user{row['Id']}", f"user{row['Id']}@example.com",
                    row['DisplayName'], row.get('WebsiteUrl', '<NULL>'), row.get('Location', '<NULL>'),
                    row.get('AboutMe', '<NULL>'), row['CreationDate'], row['Reputation'], row['Views'], row['UpVotes'],
                    row['DownVotes'], True, row['Id'] == '-1', password
                ])
        with (self.temp_dir / 'users.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE users CASCADE")
                cursor.copy_from(f, table='users', columns=(
                    'id', 'username', 'email', 'display_name', 'website_url', 'location', 'about', 'creation_date',
                    'reputation', 'views', 'up_votes', 'down_votes', 'is_active', 'is_employee', 'password'
                ), sep=',', null='<NULL>')
        self.output.write("Users loaded")

    def load_badges(self):
        """Load the badges.
        """
        self.output.write(f"Loading badges")
        badges = {
            row['Name']: {'Name': row['Name'], 'Class': row['Class'], 'TagBased': row['TagBased']}
            for row in self.iterate_xml(self.temp_dir / self.BADGES_FILE)
        }
        with (self.temp_dir / 'badges.csv').open('wt') as f:
            csv_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in badges.values():
                csv_writer.writerow([
                    row['Name'], row['Class'], row['TagBased']
                ])
        with (self.temp_dir / 'badges.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE badges CASCADE")
                cursor.copy_from(f, table='badges', columns=('name', 'badge_class', 'tag_based'), sep=',')
        self.output.write("Badges loaded")

    def load_user_badges(self):
        """Load the user badges.
        """
        self.output.write(f"Loading user badges")

        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM badges")
            badges = {row[1]: row[0] for row in cursor.fetchall()}

        user_ids = {row['Id'] for row in self.iterate_xml(self.temp_dir / self.USERS_FILE)}
        with (self.temp_dir / 'user_badges.csv').open('wt') as f:
            csv_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in self.iterate_xml(self.temp_dir / self.BADGES_FILE):
                if row['UserId'] in user_ids:
                    csv_writer.writerow([badges[row['Name']], row['UserId'], row['Date']])
        with (self.temp_dir / 'user_badges.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE user_badges CASCADE")
                cursor.copy_from(f, table='user_badges', columns=('badge_id', 'user_id', 'date_awarded'), sep=',')
        self.output.write("User badges loaded")

    def load_posts(self):
        """Load the posts.
        """
        self.output.write(f"Loading posts")
        post_ids = {row['Id'] for row in self.iterate_xml(self.temp_dir / self.POSTS_FILE)}
        with (self.temp_dir / 'posts.csv').open('wt') as f:
            csv_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in self.iterate_xml(self.temp_dir / self.POSTS_FILE):
                csv_writer.writerow([
                    row['Id'], row.get('Title', '<NULL>'), row['Body'], row['PostTypeId'], row['CreationDate'],
                    row.get('LastEditDate', '<NULL>'), row['LastActivityDate'], row['Score'],
                    row.get('ViewCount', '<NULL>'), row.get('AnswerCount', '<NULL>'), row.get('CommentCount', '<NULL>'),
                    row.get('FavoriteCount', '<NULL>'), row.get('OwnerUserId', '<NULL>'),
                    row.get('LastEditorUserId', '<NULL>'), row.get('ParentId', '<NULL>'),
                    row['AcceptedAnswerId'] if row.get('') in post_ids else '<NULL>', row['ContentLicense']
                ])
        with (self.temp_dir / 'posts.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE posts CASCADE")
                cursor.copy_from(f, table='posts', columns=(
                    'id', 'title', 'body', 'type', 'creation_date', 'last_edit_date', 'last_activity_date', 'score',
                    'view_count', 'answer_count', 'comment_count', 'favorite_count', 'owner_id', 'last_editor_id',
                    'parent_id', 'accepted_answer_id', 'content_license'
                ), sep=',', null='<NULL>')
        self.output.write(f"Posts loaded")

    def load_comments(self):
        """Load the comments.
        """
        self.output.write(f"Loading comments")
        with (self.temp_dir / 'comments.csv').open('wt') as f:
            csv_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in self.iterate_xml(self.temp_dir / self.COMMENTS_FILE):
                csv_writer.writerow([
                    row['Id'], row['PostId'], row['Score'], row['Text'], row['CreationDate'], row['ContentLicense'],
                    row.get('UserId', '<NULL>')
                ])
        with (self.temp_dir / 'comments.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE comments CASCADE")
                cursor.copy_from(f, table='comments', columns=(
                    'id', 'post_id', 'score', 'text', 'creation_date', 'content_license', 'user_id'
                ), sep=',', null='<NULL>')
        self.output.write(f"Comments loaded")

    def load_post_history(self):
        """Load the post history.
        """
        self.output.write(f"Loading post history")
        post_ids = {row['Id'] for row in self.iterate_xml(self.temp_dir / self.POSTS_FILE)}
        with (self.temp_dir / 'post_history.csv').open('wt') as f:
            csv_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in self.iterate_xml(self.temp_dir / self.POST_HISTORY_FILE):
                if row['PostId'] in post_ids:
                    csv_writer.writerow([
                        row['Id'], row['PostId'], row['PostHistoryTypeId'], row['RevisionGUID'], row['CreationDate'],
                        row.get('UserId', '<NULL>'), row.get('UserDisplayName', '<NULL>'), row.get('Comment', '<NULL>'),
                        row.get('Text', '<NULL>'), row.get('ContentLicense', '<NULL>')
                    ])
        with (self.temp_dir / 'post_history.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE post_history CASCADE")
                cursor.copy_from(f, table='post_history', columns=(
                    'id', 'post_id', 'type', 'revision_guid', 'creation_date', 'user_id', 'user_display_name',
                    'comment', 'text', 'content_license'
                ), sep=',', null='<NULL>')
        self.output.write(f"Post history loaded")

    def load_post_links(self):
        """Load the post links.
        """
        self.output.write(f"Loading post links")
        post_ids = {row['Id'] for row in self.iterate_xml(self.temp_dir / self.POSTS_FILE)}
        with (self.temp_dir / 'post_links.csv').open('wt') as f:
            csv_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in self.iterate_xml(self.temp_dir / self.POST_LINKS_FILE):
                if row['PostId'] in post_ids and row['RelatedPostId'] in post_ids:
                    csv_writer.writerow([
                        row['Id'], row['PostId'], row['RelatedPostId'], row['LinkTypeId']
                    ])
        with (self.temp_dir / 'post_links.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE post_links CASCADE")
                cursor.copy_from(f, table='post_links', columns=(
                    'id', 'post_id', 'related_post_id', 'type'
                ), sep=',', null='<NULL>')
        self.output.write(f"Post links loaded")

    def load_post_votes(self):
        """Load the post votes.
        """
        self.output.write(f"Loading post votes")
        post_ids = {row['Id'] for row in self.iterate_xml(self.temp_dir / self.POSTS_FILE)}
        with (self.temp_dir / 'post_votes.csv').open('wt') as f:
            csv_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in self.iterate_xml(self.temp_dir / self.VOTES_FILE):
                if row['PostId'] in post_ids:
                    csv_writer.writerow([
                        row['Id'], row['PostId'], row['VoteTypeId'], row.get('UserId', '<NULL>'), row['CreationDate']
                    ])
        with (self.temp_dir / 'post_votes.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE post_votes CASCADE")
                cursor.copy_from(f, table='post_votes', columns=(
                    'id', 'post_id', 'type', 'user_id', 'creation_date'
                ), sep=',', null='<NULL>')
        self.output.write(f"Post votes loaded")

    def load_tags(self):
        """Load the tags.
        """
        self.output.write(f"Loading tags")
        with (self.temp_dir / 'tags.csv').open('wt') as f:
            csv_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in self.iterate_xml(self.temp_dir / self.TAGS_FILE):
                csv_writer.writerow([
                    row['Id'], row['TagName'], row['Count'], row.get('ExcerptPostId', '<NULL>'),
                    row.get('WikiPostId', '<NULL>')
                ])
        with (self.temp_dir / 'tags.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE tags CASCADE")
                cursor.copy_from(f, table='tags', columns=(
                    'id', 'name', 'count', 'excerpt_id', 'wiki_id'
                ), sep=',', null='<NULL>')

        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM tags")
            tags = {row[1]: row[0] for row in cursor.fetchall()}
        with (self.temp_dir / 'post_tags.csv').open('wt') as f:
            csv_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in self.iterate_xml(self.temp_dir / self.POSTS_FILE):
                for match in re.finditer(r'<(.*?)>', row.get('Tags', '')):
                    csv_writer.writerow([row['Id'], tags[match.group(1)]])
        with (self.temp_dir / 'post_tags.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE post_tags CASCADE")
                cursor.copy_from(f, table='post_tags', columns=('post_id', 'tag_id'), sep=',', null='<NULL>')
        self.output.write(f"Tags loaded")

    @staticmethod
    def iterate_xml(xml_file: pathlib.Path):
        """Iterate the dump xml. For each row XML element, this method yields the element attributes and their values
        as a dictionary.

        :param xml_file: The XML file.
        """
        tree = eT.iterparse(xml_file, events=("start",))
        for event, elem in tree:
            if elem.tag == 'row':
                yield dict(elem.items())


class Command(BaseCommand):
    """Command to load the data from a dump directory.
    """
    help = 'Load the data for a stackexchange site'

    def add_arguments(self, parser: CommandParser) -> typing.NoReturn:
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
        downloader = Downloader(site, self.stdout)
        downloader.download()
        importer = Importer(downloader.dump_file, self.stdout)
        importer.do_import()
        end = time.time()
        self.stdout.write(f"Data loaded, took {datetime.timedelta(seconds=end-start)}")
