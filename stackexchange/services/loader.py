"""Class for loading site data.
"""
import abc
import csv
import logging
import pathlib
import re
import tempfile

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import connection
import py7zr

from stackexchange import enums, models
from . import dowloader, siteinfo, xmlparser

# The module logger
logger = logging.getLogger(__name__)

# The regex to find tags in the posts file
TAGS_REGEX = re.compile(r'<(?P<tag_name>.*?)>')


class BaseFileLoader:
    """The base class for file loading.
    """
    def __init__(self, data_dir: pathlib.Path) -> None:
        """Create the file loader.

        :param data_dir: The data directory.
        """
        self.data_dir = data_dir

    @abc.abstractmethod
    def load(self) -> None:
        """Load the data.
        """


class UserLoader(BaseFileLoader):
    """The user loader.
    """
    def load(self) -> None:
        """Load the users.
        """
        users = set(models.User.objects.values_list('pk', flat=True))
        logger.info("Extracting users")
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
                    if user_id not in users:
                        users_writer.writerow([
                            user_id, 'admin' if user_id == -1 else f"user{row['AccountId']}",
                            make_password('admin') if user_id == -1 else '', '<NULL>', user_id == -1
                        ])
                        users.add(user_id)

                site_users_writer.writerow([
                    row['Id'], '<NULL>' if user_id is None else user_id, row['DisplayName'],
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
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE site_users CASCADE')
            with (self.data_dir / 'site_users.csv').open('rt') as site_users_file:
                cursor.copy_from(
                    site_users_file, table='site_users', columns=(
                        'id', 'user_id', 'display_name', 'website_url', 'location', 'about',
                        'creation_date', 'last_access_date', 'reputation', 'views', 'up_votes', 'down_votes'
                    ), sep=',', null='<NULL>')


class BadgeLoader(BaseFileLoader):
    """The badge loader.
    """
    def load(self) -> None:
        """Load the badges.
        """
        # First pass - load badges
        logger.info("Extracting badges")
        badge_names = set()
        with (self.data_dir / 'badges.csv').open('wt') as badges_file:
            badges_writer = csv.writer(badges_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Badges.xml'):
                if row['Name'] not in badge_names:
                    badges_writer.writerow([
                        row['Name'], row['Class'],
                        enums.BadgeType.TAG_BASED.value if row['TagBased'] == 'True' else enums.BadgeType.NAMED.value
                    ])
                    badge_names.add(row['Name'])

        logger.info("Loading badges")
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE badges CASCADE')
            with (self.data_dir / 'badges.csv').open('rt') as badges_file:
                cursor.copy_from(
                    badges_file, table='badges', columns=('name', 'badge_class', 'badge_type'), sep=',',
                    null='<NULL>')

        # Second pass - load user badges
        logger.info("Extracting user badges")
        badge_ids = {b['name']: b['pk'] for b in models.Badge.objects.values('pk', 'name')}
        with (self.data_dir / 'user_badges.csv').open('wt') as user_badges_file:
            user_badges_writer = csv.writer(user_badges_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Badges.xml'):
                user_badges_writer.writerow([
                    row['UserId'], badge_ids[row['Name']], row['Date']
                ])

        logger.info("Loading user badges")
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE user_badges CASCADE')
            with (self.data_dir / 'user_badges.csv').open('rt') as user_badges_file:
                cursor.copy_from(
                    user_badges_file, table='user_badges', columns=('user_id', 'badge_id', 'date_awarded'),
                    sep=',', null='<NULL>')


class PostLoader(BaseFileLoader):
    """The post loader.
    """
    def load(self) -> None:
        """Load the posts.
        """
        logger.info("Extracting posts")
        with (self.data_dir / 'posts.csv').open('wt') as posts_file:
            posts_writer = csv.writer(posts_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Posts.xml'):
                posts_writer.writerow([
                    row['Id'], row.get('ParentId', '<NULL>'), row.get('AcceptedAnswerId', '<NULL>'),
                    row.get('OwnerUserId', '<NULL>'), row.get('LastEditorUserId', '<NULL>'), row['PostTypeId'],
                    row.get('Title', '<NULL>'), row['Body'], row.get('LastEditorDisplayName', '<NULL>'),
                    row['CreationDate'], row.get('LastEditDate', '<NULL>'), row['LastActivityDate'],
                    row.get('CommunityOwnedDate', '<NULL>'), row.get('ClosedDate', '<NULL>'), row['Score'],
                    row.get('ViewCount', 0), row.get('AnswerCount', 0), row.get('CommentCount', 0),
                    row.get('FavoriteCount', 0), row['ContentLicense']
                ])

        logger.info("Loading posts")
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE posts CASCADE')
            with (self.data_dir / 'posts.csv').open('rt') as posts_file:
                cursor.copy_from(
                    posts_file, table='posts', columns=(
                        'id', 'question_id', 'accepted_answer_id', 'owner_id', 'last_editor_id', 'type', 'title',
                        'body', 'last_editor_display_name', 'creation_date', 'last_edit_date', 'last_activity_date',
                        'community_owned_date', 'closed_date', 'score', 'view_count', 'answer_count', 'comment_count',
                        'favorite_count', 'content_license'
                    ), sep=',', null='<NULL>')


class TagLoader(BaseFileLoader):
    """The tag loader.
    """
    def load(self) -> None:
        """Load the tags.
        """
        logger.info("Extracting tags")
        with (self.data_dir / 'tags.csv').open('wt') as tags_file:
            tags_writer = csv.writer(tags_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Tags.xml'):
                tags_writer.writerow([
                    row['Id'], row['TagName'], row['Count'], row.get('ExcerptPostId', '<NULL>'),
                    row.get('WikiPostId', '<NULL>')
                ])

        logger.info("Loading tags")
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE tags CASCADE')
            with (self.data_dir / 'tags.csv').open('rt') as tags_file:
                cursor.copy_from(
                    tags_file, table='tags', columns=('id', 'name', 'award_count', 'excerpt_id', 'wiki_id'), sep=',',
                    null='<NULL>')

        tag_ids = {t['name']: t['pk'] for t in models.Tag.objects.values('pk', 'name')}
        logger.info("Extracting post tags")
        with (self.data_dir / 'post_tags.csv').open('wt') as post_tags_file:
            post_tags_writer = csv.writer(post_tags_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Posts.xml'):
                for match in TAGS_REGEX.finditer(row.get('Tags', '')):
                    post_tags_writer.writerow([row['Id'], tag_ids[match.group('tag_name')]])

        logger.info("Loading post tags")
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE post_tags CASCADE')
            with (self.data_dir / 'post_tags.csv').open('rt') as post_tags_file:
                cursor.copy_from(
                    post_tags_file, table='post_tags', columns=('post_id', 'tag_id'), sep=',', null='<NULL>')


class PostVoteLoader(BaseFileLoader):
    """The post vote loader.
    """
    def load(self) -> None:
        """Load the post votes.
        """
        logger.info("Extracting post votes")
        post_ids = set(models.Post.objects.values_list('pk', flat=True))
        with (self.data_dir / 'post_votes.csv').open('wt') as post_votes_file:
            post_votes_writer = csv.writer(post_votes_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Votes.xml'):
                if int(row['PostId']) in post_ids:
                    post_votes_writer.writerow([
                        row['Id'], row['PostId'], row['VoteTypeId'], row['CreationDate'], row.get('UserId', '<NULL>'),
                        row.get('BountyAmount', '<NULL>')
                    ])

        logger.info("Loading post votes")
        with (self.data_dir / 'post_votes.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE post_votes CASCADE")
                cursor.copy_from(f, table='post_votes', columns=(
                    'id', 'post_id', 'type', 'creation_date', 'user_id', 'bounty_amount'
                ), sep=',', null='<NULL>')


class PostHistoryLoader(BaseFileLoader):
    """The post history loader.
    """
    def load(self) -> None:
        """Load the post history.
        """
        logger.info("Extracting post history")
        with (self.data_dir / 'post_history.csv').open('wt') as post_history_file:
            post_history_writer = csv.writer(post_history_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'PostHistory.xml'):
                post_history_writer.writerow([
                    row['Id'], row['PostHistoryTypeId'], row['PostId'], row['RevisionGUID'], row['CreationDate'],
                    row.get('UserId', '<NULL>'), row.get('UserDisplayName', '<NULL>'), row.get('Comment', '<NULL>'),
                    row.get('Text', '<NULL>'), row.get('ContentLicense', '<NULL>')
                ])

        logger.info("Loading post history")
        with (self.data_dir / 'post_history.csv').open('rt') as f:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE post_history CASCADE")
                cursor.copy_from(f, table='post_history', columns=(
                    'id', 'type', 'post_id', 'revision_guid', 'creation_date', 'user_id', 'user_display_name',
                    'comment', 'text', 'content_license'
                ), sep=',', null='<NULL>')


class SiteDataLoader:
    """Helper class to load site data
    """
    LOADERS = (UserLoader, BadgeLoader, PostLoader, TagLoader, PostVoteLoader, PostHistoryLoader)

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

            for loader_class in self.LOADERS:
                loader = loader_class(data_dir=pathlib.Path(temp_dir))
                loader.load()

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
