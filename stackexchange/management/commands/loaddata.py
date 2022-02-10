import csv
import datetime
import io
import pathlib
import re
import time
import tempfile
import typing
import xml.etree.ElementTree as eT

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandParser
from django.db import connection, transaction, utils
from django.conf import settings
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

    @staticmethod
    def _get_indexes() -> dict:
        """Get all database indexes.

        :return: A dictionary with the index name as a key and the index definition as a value.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT indexname, indexdef FROM pg_indexes WHERE schemaname = 'public'")

            return {row[0]: row[1] for row in cursor.fetchall()}

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

    def import_file(self):
        """Import files to the database.
        """
        self.drop_indexes()
        with tempfile.TemporaryDirectory() as temp_dir:
            self.output.write("Extracting dump")
            with py7zr.SevenZipFile(self.dump_file, mode='r') as dump_file:
                dump_file.extractall(path=temp_dir)
            self.output.write("Dump extracted")
            self.temp_dir = pathlib.Path(temp_dir)
            self.load_users()
            # self.load_badges(temp_dir / self.BADGES_FILE)
            # self.load_posts(temp_dir / self.POSTS_FILE)
            # self.load_comments(temp_dir / self.COMMENTS_FILE)
            # self.load_post_history(temp_dir / self.POST_HISTORY_FILE)
            # self.load_post_links(temp_dir / self.POST_LINKS_FILE)
            # self.load_post_votes(temp_dir / self.VOTES_FILE)
            # self.load_tags(temp_dir / self.TAGS_FILE, temp_dir / self.POSTS_FILE)
        self.recreate_indexes()

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
                    row['DisplayName'], row.get('WebsiteUrl'), row.get('Location'), row.get('About'),
                    row['CreationDate'], row['Reputation'], row['Views'], row['UpVotes'],
                    row['DownVotes'], True, row['Id'] == '-1', password
                ])
        with (self.temp_dir / 'users.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE users CASCADE")
                cursor.copy_from(f, table='users', columns=(
                    'id', 'username', 'email', 'display_name', 'website_url', 'location', 'about', 'creation_date',
                    'reputation', 'views', 'up_votes', 'down_votes', 'is_active', 'is_employee', 'password'
                ), sep=',')
        self.output.write("Users loaded")

    def load_badges(self, badges_file: pathlib.Path):
        """Load the badges.

        :param badges_file: The badges file.
        """
        self.output.write(f"Loading badges")
        badges = {
            row['Name']: {'Name': row['Name'], 'Class': row['Class'], 'TagBased': row['TagBased']}
            for row in self.iterate_xml(badges_file)
        }
        with connection.cursor() as cursor:
            with transaction.atomic():
                self.insert_data(data=badges.values(), cursor=cursor, table_name='badges', table_columns=(
                    'name', 'badge_class', 'tag_based'
                ), params=lambda x: (x['Name'], x['Class'], x['TagBased']))
            # Map badge ids to names
            cursor.execute("SELECT id, name FROM badges")
            badges = {row[1]: row[0] for row in cursor.fetchall()}
            # Get all user ids
            cursor.execute("SELECT id FROM users")
            users = {row[0] for row in cursor.fetchall()}
            with transaction.atomic():
                self.insert_data(
                    data=self.iterate_xml(badges_file), cursor=cursor, table_name='user_badges',
                    table_columns=('badge_id', 'user_id', 'date_awarded'), params=lambda row: (
                        badges[row['Name']], row['UserId'], row['Date']
                    ) if int(row['UserId']) in users else None
                )
        self.output.write(f"Badges loaded")

    def load_posts(self, posts_file: pathlib.Path):
        """Load the posts.

        :param posts_file: The posts file.
        """
        self.output.write(f"Loading posts")
        with connection.cursor() as cursor:
            with transaction.atomic():
                row_ids = {row['Id'] for row in self.iterate_xml(posts_file)}
                self.insert_data(data=self.iterate_xml(posts_file), cursor=cursor, table_name='posts', table_columns=(
                    'id', 'title', 'body', 'type', 'creation_date', 'last_edit_date', 'last_activity_date', 'score',
                    'view_count', 'answer_count', 'comment_count', 'favorite_count', 'content_license', 'owner_id',
                    'last_editor_id', 'parent_id', 'accepted_answer_id'
                ), params=lambda row: (
                    row['Id'], row.get('Title'), row['Body'], row['PostTypeId'], row['CreationDate'],
                    row.get('LastEditDate'), row['LastActivityDate'], row['Score'], row.get('ViewCount'),
                    row.get('AnswerCount'), row.get('CommentCount'), row.get('FavoriteCount'), row['ContentLicense'],
                    row.get('OwnerUserId'), row.get('LastEditorUserId'), row.get('ParentId'),
                    row.get('AcceptedAnswerId') if row.get('AcceptedAnswerId') in row_ids else None
                ))
        self.output.write(f"Posts loaded")

    def load_comments(self, comments_file: pathlib.Path):
        """Load the comments.

        :param comments_file: The comments file.
        """
        self.output.write(f"Loading comments")
        with connection.cursor() as cursor:
            with transaction.atomic():
                self.insert_data(
                    data=self.iterate_xml(comments_file), cursor=cursor, table_name='comments',
                    table_columns=('id', 'post_id', 'score', 'text', 'creation_date', 'content_license', 'user_id'),
                    params=lambda row: (
                        row['Id'], row['PostId'], row['Score'], row['Text'], row['CreationDate'], row['ContentLicense'],
                        row.get('UserId')
                    )
                )
        self.output.write(f"Comments loaded")

    def load_post_history(self, post_history_file: pathlib.Path):
        """Load the post history.

        :param post_history_file: The post history file.
        """
        self.output.write(f"Loading post history")
        with connection.cursor() as cursor:
            with transaction.atomic():
                cursor.execute("SELECT id FROM posts")
                post_ids = {row[0] for row in cursor.fetchall()}

                self.insert_data(
                    data=self.iterate_xml(post_history_file), cursor=cursor, table_name='post_history',
                    table_columns=(
                        'id', 'post_id', 'type', 'revision_guid', 'creation_date', 'user_id', 'user_display_name',
                        'comment', 'text', 'content_license'
                    ), params=lambda row: (
                        row['Id'], row['PostId'], row['PostHistoryTypeId'], row['RevisionGUID'], row['CreationDate'],
                        row.get('UserId'), row.get('UserDisplayName'), row.get('Comment'), row.get('Text'),
                        row.get('ContentLicense')
                    ) if int(row['PostId']) in post_ids else None
                )
        self.output.write(f"Post history loaded")

    def load_post_links(self, post_links_file: pathlib.Path):
        """Load the post links.

        :param post_links_file: The post links file.
        """
        self.output.write(f"Loading post links")
        with connection.cursor() as cursor:
            with transaction.atomic():
                cursor.execute("SELECT id FROM posts")
                post_ids = {row[0] for row in cursor.fetchall()}

                self.insert_data(
                    data=self.iterate_xml(post_links_file), cursor=cursor, table_name='post_links',
                    table_columns=('id', 'post_id', 'related_post_id', 'type'),
                    params=lambda row: (
                        row['Id'], row['PostId'], row['RelatedPostId'], row['LinkTypeId']
                    ) if int(row['PostId']) in post_ids and int(row['RelatedPostId']) in post_ids else None
                )
        self.output.write(f"Post links loaded")

    def load_post_votes(self, post_votes_file: pathlib.Path):
        """Load the post votes.

        :param post_votes_file: The post votes file.
        """
        self.output.write(f"Loading post votes")
        with connection.cursor() as cursor:
            with transaction.atomic():
                cursor.execute("SELECT id FROM posts")
                post_ids = {row[0] for row in cursor.fetchall()}

                self.insert_data(
                    data=self.iterate_xml(post_votes_file), cursor=cursor, table_name='post_votes',
                    table_columns=('id', 'post_id', 'type', 'user_id', 'creation_date'),
                    params=lambda row: (
                        row['Id'], row['PostId'], row['VoteTypeId'], row.get('UserId'), row['CreationDate']
                    ) if int(row['PostId']) in post_ids else None
                )
        self.output.write(f"Post votes loaded")

    def load_tags(self, tags_file: pathlib.Path, posts_file: pathlib.Path):
        """Load the tags.

        :param tags_file: The tags file.
        :param posts_file: The posts file.
        """
        self.output.write(f"Loading tags")
        with connection.cursor() as cursor:
            with transaction.atomic():
                self.insert_data(
                    data=self.iterate_xml(tags_file), cursor=cursor, table_name='tags',
                    table_columns=('id', 'name', 'count', 'excerpt_id', 'wiki_id'),
                    params=lambda row: (
                        row['Id'], row['TagName'], row['Count'], row.get('ExcerptPostId'), row.get('WikiPostId')
                    )
                )
            with transaction.atomic():
                self.insert_data(data=self.yield_post_tags(cursor, posts_file), cursor=cursor, table_name='post_tags',
                                 table_columns=('post_id', 'tag_id'), params=lambda row: (row['PostId'], row['TagId']))
        self.output.write(f"Tags loaded")

    def yield_post_tags(self, cursor, posts_file: pathlib.Path):
        cursor.execute("SELECT id, name FROM tags")
        tags = {row[1]: row[0] for row in cursor.fetchall()}

        for row in self.iterate_xml(posts_file):
            for match in re.finditer(r'<(.*?)>', row.get('Tags', '')):
                yield {'PostId': row['Id'], 'TagId': tags[match.group(1)]}

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

    def insert_data(self, data, cursor, table_name: str, table_columns: typing.Collection[str], params):
        """Insert data to the database

        :param data: The data to insert.
        :param cursor:
        :param table_name: The name of the table to insert the data to.
        :param table_columns: The name of the table columns.
        :param params:
        """
        # Clear data before inserting
        self.output.write(f"Truncating table {table_name}")
        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")
        self.output.write(f"Inserting data for table {table_name}")
        rows_inserted = 0
        for row in data:
            if params(row):
                cursor.execute(f"""
                    INSERT INTO {table_name}({','.join(table_columns)})
                    VALUES ({','.join('%s' for _ in range(len(table_columns)))})
                """, params(row))
                rows_inserted += 1
        self.output.write(f"{rows_inserted} rows inserted")


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
        importer.import_file()
        end = time.time()
        self.stdout.write(f"Data loaded, took {datetime.timedelta(seconds=end-start)}")
