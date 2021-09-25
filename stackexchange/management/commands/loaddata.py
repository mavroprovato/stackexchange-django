import datetime
import pathlib
import re
import time
import shutil
import typing
import xml.etree.ElementTree as eT

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandParser
from django.db import connection, transaction
from django.conf import settings
import requests
import py7zr


class Command(BaseCommand):
    """Command to load the data from a dump directory.
    """
    help = 'Load the data from a dump directory'

    def add_arguments(self, parser: CommandParser) -> typing.NoReturn:
        """Add the command arguments.

        :param parser: The argument parser.
        """
        parser.add_argument("community", help="The name of the community to download")

    def handle(self, *args, **options):
        """Implements the logic of the command.

        :param args: The arguments.
        :param options: The options.
        """
        community = options['community']
        start = time.time()
        self.stdout.write(f"Loading data for {community}")
        dump_dir = self.download(community)
        self.load_users(dump_dir / "Users.xml")
        self.load_badges(dump_dir / "Badges.xml")
        self.load_posts(dump_dir / "Posts.xml")
        self.load_comments(dump_dir / "Comments.xml")
        self.load_post_history(dump_dir / "PostHistory.xml")
        self.load_post_links(dump_dir / "PostLinks.xml")
        self.load_post_votes(dump_dir / "Votes.xml")
        self.load_tags(dump_dir / "Tags.xml", dump_dir / "Posts.xml")
        end = time.time()
        self.stdout.write(f"Data loaded, took {datetime.timedelta(seconds=end-start)}")

    def download(self, community: str) -> pathlib.Path:
        """Download the dump for the community.

        :param community: The community name.
        :return: The dump directory with the extracted files.
        """
        url = f"https://archive.org/download/stackexchange/{community}.com.7z"
        var_dir = pathlib.Path(settings.BASE_DIR) / "var"
        var_dir.mkdir(parents=True, exist_ok=True)

        # Download file if needed
        dump_file = var_dir / f"{community}.com.7z"
        if not dump_file.exists():
            self.stdout.write("Downloading dump file")
            with requests.get(url, stream=True) as r:
                with open(var_dir / f"{community}.com.7z", 'wb') as f:
                    shutil.copyfileobj(r.raw, f)

        # Extract the file
        extract_path = var_dir / community
        if not extract_path.exists():
            self.stdout.write("Extracting dump")
            with py7zr.SevenZipFile(dump_file, mode='r') as dump_file:
                dump_file.extractall(path=extract_path)

        return extract_path

    def load_users(self, users_file: pathlib.Path):
        """Load the users.

        :param users_file: The users file.
        """
        self.stdout.write(f"Loading users")
        password = make_password("password")
        with connection.cursor() as cursor:
            with transaction.atomic():
                self.insert_data(data=self.iterate_xml(users_file), cursor=cursor, table_name='users', table_columns=(
                    'id', 'display_name', 'website_url', 'location', 'about', 'creation_date', 'reputation', 'views',
                    'up_votes', 'down_votes', 'username', 'email', 'password', 'is_active', 'is_employee'
                ), params=lambda row: (
                    row['Id'], row['DisplayName'], row.get('WebsiteUrl'), row.get('Location'), row.get('AboutMe'),
                    row['CreationDate'], row['Reputation'], row['Views'], row['UpVotes'], row['DownVotes'],
                    'admin' if row['Id'] == '-1' else f"user{row['Id']}", f"user{row['Id']}@example.com", password,
                    True, row['Id'] == '-1'
                ))
        self.stdout.write(f"Users loaded")

    def load_badges(self, badges_file: pathlib.Path):
        """Load the badges.

        :param badges_file: The badges file.
        """
        self.stdout.write(f"Loading badges")
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
                    ) if row['UserId'] in users else None
                )
        self.stdout.write(f"Badges loaded")

    def load_posts(self, posts_file: pathlib.Path):
        """Load the posts.

        :param posts_file: The posts file.
        """
        self.stdout.write(f"Loading posts")
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
        self.stdout.write(f"Posts loaded")

    def load_comments(self, comments_file: pathlib.Path):
        """Load the comments.

        :param comments_file: The comments file.
        """
        self.stdout.write(f"Loading comments")
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
        self.stdout.write(f"Comments loaded")

    def load_post_history(self, post_history_file: pathlib.Path):
        """Load the post history.

        :param post_history_file: The post history file.
        """
        self.stdout.write(f"Loading post history")
        with connection.cursor() as cursor:
            with transaction.atomic():
                self.insert_data(
                    data=self.iterate_xml(post_history_file), cursor=cursor, table_name='post_history',
                    table_columns=(
                        'id', 'post_id', 'type', 'revision_guid', 'creation_date', 'user_id', 'user_display_name',
                        'comment', 'text', 'content_license'
                    ), params=lambda row: (
                        row['Id'], row['PostId'], row['PostHistoryTypeId'], row['RevisionGUID'], row['CreationDate'],
                        row.get('UserId'), row.get('UserDisplayName'), row.get('Comment'), row.get('Text'),
                        row.get('ContentLicense')
                    )
                )
        self.stdout.write(f"Post history loaded")

    def load_post_links(self, post_links_file: pathlib.Path):
        """Load the post links.

        :param post_links_file: The post links file.
        """
        self.stdout.write(f"Loading post links")
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
        self.stdout.write(f"Post links loaded")

    def load_post_votes(self, post_votes_file: pathlib.Path):
        """Load the post votes.

        :param post_votes_file: The post votes file.
        """
        self.stdout.write(f"Loading post votes")
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
        self.stdout.write(f"Post votes loaded")

    def load_tags(self, tags_file: pathlib.Path, posts_file: pathlib.Path):
        """Load the tags.

        :param tags_file: The tags file.
        :param posts_file: The posts file.
        """
        self.stdout.write(f"Loading tags")
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
        self.stdout.write(f"Tags loaded")

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

    @staticmethod
    def insert_data(data, cursor, table_name: str, table_columns: typing.Collection[str], params):
        """Insert data to the database

        :param data: The data to insert.
        :param cursor:
        :param table_name: The name of the table to insert the data to.
        :param table_columns: The name of the table columns.
        :param params:
        """
        # Clear data before inserting
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        for row in data:
            if params(row):
                cursor.execute(f"""
                    INSERT INTO {table_name}({','.join(table_columns)})
                    VALUES ({','.join('%s' for _ in range(len(table_columns)))})
                """, params(row))
