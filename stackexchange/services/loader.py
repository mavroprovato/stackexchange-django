"""Class for loading site data.
"""
import abc
from collections.abc import Iterable
import csv
import datetime
import logging
import pathlib
import tempfile
import time

from django.conf import settings
from django.db import connection
import py7zr
import requests

from stackexchange import enums, models
from . import dowloader, siteinfo, xmlparser

# The module logger
logger = logging.getLogger(__name__)


class BaseFileLoader:
    """The base class for file loading.
    """
    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Create the file loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory.
        """
        self.site_id = site_id
        self.data_dir = data_dir

    @abc.abstractmethod
    def load(self) -> None:
        """Load the data.
        """
        raise NotImplementedError

    def extract_table_data(self, input_filename: str, output_filename: str, transform_function) -> None:
        """Extract the data from an input file.

        :param input_filename: The input filename.
        :param output_filename: The output filename.
        :param transform_function: The transform function.
        """
        with (self.data_dir / output_filename).open('wt') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / input_filename):
                transformed_row = transform_function(row)
                if transformed_row:
                    writer.writerow(transformed_row)

    def load_table_data(self, filename: str, table_name: str, columns: Iterable[str], truncate: bool = True) -> None:
        """Load data for a table from a CSV file.

        :param filename: The name of the CSV file.
        :param table_name: The name of the table to load.
        :param columns: The table columns.
        :param truncate: True to truncate data before loading.
        """
        logger.info("Loading table %s", table_name)

        with connection.cursor() as cursor:
            if truncate:
                cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
            with (self.data_dir / filename).open('rt') as f:
                cursor.copy_from(f, table=table_name, columns=columns, sep=',', null='<NULL>')


class UserLoader(BaseFileLoader):
    """The user loader.
    """
    def transform_users(self, row):
        """Transform the input row so that it can be loaded to the users table.

        :param row: The input row.
        :return: The transformed row.
        """
        return (
            row['Id'], self.site_id, row['DisplayName'], row.get('WebsiteUrl', '<NULL>'), row.get('Location', '<NULL>'),
            row.get('AboutMe', '<NULL>'), row['CreationDate'], datetime.datetime.now(), row['LastAccessDate'],
            row['Reputation'], row['Views'], row['UpVotes'], row['DownVotes']
        )

    def load(self) -> None:
        """Load the users.
        """
        logger.info("Extracting users")
        self.extract_table_data(
            input_filename='Users.xml', output_filename='site_users.csv', transform_function=self.transform_users
        )
        self.load_table_data(
            filename='site_users.csv', table_name='site_users', columns=(
                'unique_id', 'site_id', 'display_name', 'website_url', 'location', 'about', 'creation_date',
                'last_modified_date', 'last_access_date', 'reputation', 'views', 'up_votes', 'down_votes'
            )
        )


class BadgeLoader(BaseFileLoader):
    """The badge loader.
    """
    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Initialize the badge loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory
        """
        super().__init__(site_id, data_dir)
        self.users = set(models.SiteUser.objects.values_list('pk', flat=True))
        self.processed_badges = set()
        self.badges = []

    def transform_badges(self, row: dict) -> Iterable[str] | None:
        """Transform the input row so that it can be loaded to the badges table.

        :param row: The input row.
        :return: The transformed row.
        """
        if row['Name'] in self.processed_badges:
            return None
        self.processed_badges.add(row['Name'])

        return (
            row['Id'], row['Name'], row['Class'],
            enums.BadgeType.TAG_BASED.value if row['TagBased'] == 'True' else enums.BadgeType.NAMED.value
        )

    def transform_user_badges(self, row: dict) -> Iterable[str] | None:
        """Transform the input row so that it can be loaded to the user_badges table.

        :param row: The input row.
        :return: The transformed row.
        """
        if int(row['UserId']) in self.users:
            return row['UserId'], self.badges[row['Name']], row['Date']

        return None

    def load(self) -> None:
        """Load the badges.
        """
        self.extract_table_data(
            input_filename='Badges.xml', output_filename='badges.csv', transform_function=self.transform_badges
        )
        self.load_table_data(
            filename='badges.csv', table_name='badges', columns=('id', 'name', 'badge_class', 'badge_type')
        )

        self.badges = {b['name']: b['pk'] for b in models.Badge.objects.values('pk', 'name')}

        self.extract_table_data(
            input_filename='Badges.xml', output_filename='user_badges.csv',
            transform_function=self.transform_user_badges
        )
        self.load_table_data(
            filename='user_badges.csv', table_name='user_badges', columns=('user_id', 'badge_id', 'date_awarded')
        )


class PostLoader(BaseFileLoader):
    """The post loader.
    """
    def load(self) -> None:
        """Load the posts.
        """
        logger.info("Extracting posts")
        post_ids = {row['Id'] for row in xmlparser.XmlFileIterator(self.data_dir / 'Posts.xml')}
        users = {user['unique_id']: user['pk'] for user in models.SiteUser.objects.values('pk', 'unique_id')}
        with (self.data_dir / 'posts.csv').open('wt') as posts_file:
            posts_writer = csv.writer(posts_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Posts.xml'):
                posts_writer.writerow([
                    row['Id'], row.get('ParentId', '<NULL>'),
                    row['AcceptedAnswerId'] if row.get('AcceptedAnswerId') in post_ids else '<NULL>',
                    users[row['OwnerUserId']] if row.get('OwnerUserId') in users else '<NULL>',
                    users[row['LastEditorUserId']] if row.get('LastEditorUserId') in users else '<NULL>',
                    row['PostTypeId'], row.get('Title', '<NULL>'), row['Body'],
                    row.get('LastEditorDisplayName', '<NULL>'), row['CreationDate'], row.get('LastEditDate', '<NULL>'),
                    row['LastActivityDate'], row.get('CommunityOwnedDate', '<NULL>'), row.get('ClosedDate', '<NULL>'),
                    row['Score'], row.get('ViewCount', 0), row.get('AnswerCount', 0), row.get('CommentCount', 0),
                    row.get('FavoriteCount', 0), row.get('ContentLicense', enums.ContentLicense.CC_BY_SA_4_0.value)
                ])

        self.load_table_data(
            filename='posts.csv', table_name='posts', columns=(
                'id', 'question_id', 'accepted_answer_id', 'owner_id', 'last_editor_id', 'type', 'title', 'body',
                'last_editor_display_name', 'creation_date', 'last_edit_date', 'last_activity_date',
                'community_owned_date', 'closed_date', 'score', 'view_count', 'answer_count', 'comment_count',
                'favorite_count', 'content_license'
            )
        )


class TagLoader(BaseFileLoader):
    """The tag loader.
    """
    # The base URL of the official StackExchange API
    STACKEXCHANGE_API_BASE_URL = 'https://api.stackexchange.com/2.3'

    def load(self) -> None:
        """Load the tags.
        """
        logger.info("Extracting tags")
        with (self.data_dir / 'tags.csv').open('wt') as tags_file:
            tags_writer = csv.writer(tags_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Tags.xml'):
                tags_writer.writerow([
                    row['Id'], row['TagName'], row['Count'], row.get('ExcerptPostId', '<NULL>'),
                    row.get('WikiPostId', '<NULL>'), row.get('IsRequired') == 'True', row.get('ModeratorOnly') == 'True'
                ])
        self.load_table_data(
            filename='tags.csv', table_name='tags', columns=(
                'id', 'name', 'award_count', 'excerpt_id', 'wiki_id', 'required', 'moderator_only'
            )
        )

        logger.info("Updating tag flags")
        for tag_flag in enums.TagFlag:
            tag_names = self.get_tag_names(tag_flag)
            for tag_name in tag_names:
                tag = models.Tag.objects.filter(name=tag_name).first()
                if tag is not None:
                    setattr(tag, tag_flag.attribute_name, True)
                    tag.save()

        tag_ids = {t['name']: t['pk'] for t in models.Tag.objects.values('pk', 'name')}
        logger.info("Extracting post tags")
        with (self.data_dir / 'post_tags.csv').open('wt') as post_tags_file:
            post_tags_writer = csv.writer(post_tags_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Posts.xml'):
                for tag_name in row.get('Tags', '').split('|'):
                    if tag_name and tag_name in tag_ids:
                        post_tags_writer.writerow([row['Id'], tag_ids[tag_name]])
        self.load_table_data(filename='post_tags.csv', table_name='post_tags', columns=('post_id', 'tag_id'))

    def get_tag_names(self, tag_flag: enums.TagFlag) -> Iterable[str]:
        """Returns the names of the tags that have the given flag.

        :param tag_flag: The tag flag.
        :return: An iterable of tag names that have the given flag set.
        """
        page = 1
        tags = []

        while True:
            response = requests.get(
                f"{self.STACKEXCHANGE_API_BASE_URL}/tags/{tag_flag.api_path}",
                params={'page': page, 'pagesize': 100, 'site': 'meta.math'}, timeout=60
            )
            response.raise_for_status()
            response_data = response.json()
            tags += [item['name'] for item in response_data['items']]
            if not response_data['has_more']:
                break
            page += 1
            time.sleep(1)

        return tags


class PostVoteLoader(BaseFileLoader):
    """The post vote loader.
    """
    def load(self) -> None:
        """Load the post votes.
        """
        logger.info("Extracting post votes")
        post_ids = set(models.Post.objects.values_list('pk', flat=True))
        users = {user['unique_id']: user['pk'] for user in models.SiteUser.objects.values('pk', 'unique_id')}
        with (self.data_dir / 'post_votes.csv').open('wt') as post_votes_file:
            post_votes_writer = csv.writer(post_votes_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Votes.xml'):
                if int(row['PostId']) in post_ids:
                    post_votes_writer.writerow([
                        row['Id'], row['PostId'], row['VoteTypeId'], row['CreationDate'],
                        users[row['UserId']] if row.get('UserId') in users else '<NULL>',
                        row.get('BountyAmount', '<NULL>')
                    ])
        self.load_table_data(
            filename='post_votes.csv', table_name='post_votes', columns=(
                'id', 'post_id', 'type', 'creation_date', 'user_id', 'bounty_amount'
            )
        )


class PostCommentLoader(BaseFileLoader):
    """The post comment loader.
    """
    def load(self) -> None:
        """Load the post comments.
        """
        logger.info("Extracting post comments")
        users = {user['unique_id']: user['pk'] for user in models.SiteUser.objects.values('pk', 'unique_id')}
        with (self.data_dir / 'post_comments.csv').open('wt') as post_comments_file:
            csv_writer = csv.writer(post_comments_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Comments.xml'):
                csv_writer.writerow([
                    row['Id'], row['PostId'], row['Score'], row['Text'], row['CreationDate'],
                    row.get('ContentLicense', enums.ContentLicense.CC_BY_SA_4_0.value),
                    users[row['UserId']] if row.get('UserId') in users else '<NULL>',
                    row.get('UserDisplayName', '<NULL>')
                ])
        self.load_table_data(
            filename='post_comments.csv', table_name='post_comments', columns=(
                'id', 'post_id', 'score', 'text', 'creation_date', 'content_license', 'user_id', 'user_display_name'
            )
        )


class PostHistoryLoader(BaseFileLoader):
    """The post history loader.
    """
    def load(self) -> None:
        """Load the post history.
        """
        logger.info("Extracting post history")
        with (self.data_dir / 'post_history.csv').open('wt') as post_history_file:
            users = {user['unique_id']: user['pk'] for user in models.SiteUser.objects.values('pk', 'unique_id')}
            post_ids = set(models.Post.objects.values_list('pk', flat=True))
            post_history_writer = csv.writer(post_history_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'PostHistory.xml'):
                if int(row['PostId']) in post_ids:
                    post_history_writer.writerow([
                        row['Id'], row['PostHistoryTypeId'], row['PostId'], row['RevisionGUID'], row['CreationDate'],
                        users[row['UserId']] if row.get('UserId') in users else '<NULL>',
                        row.get('UserDisplayName', '<NULL>'), row.get('Comment', '<NULL>'),
                        row.get('Text', '<NULL>'), row.get('ContentLicense', enums.ContentLicense.CC_BY_SA_4_0.value)
                    ])
        self.load_table_data(
            filename='post_history.csv', table_name='post_history', columns=(
                'id', 'type', 'post_id', 'revision_guid', 'creation_date', 'user_id', 'user_display_name', 'comment',
                'text', 'content_license'
            )
        )


class PostLinkLoader(BaseFileLoader):
    """The post link loader.
    """
    def load(self) -> None:
        """Load the post links.
        """
        logger.info("Extracting post links")
        post_ids = set(models.Post.objects.values_list('pk', flat=True))
        with (self.data_dir / 'post_links.csv').open('wt') as post_links_file:
            post_links_writer = csv.writer(post_links_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'PostLinks.xml'):
                if int(row['PostId']) in post_ids and int(row['RelatedPostId']) in post_ids:
                    post_links_writer.writerow([
                        row['Id'], row['PostId'], row['RelatedPostId'], row['LinkTypeId']
                    ])
        self.load_table_data(
            filename='post_links.csv', table_name='post_links', columns=('id', 'post_id', 'related_post_id', 'type')
        )


class SiteDataLoader:
    """Helper class to load site data
    """
    LOADERS = (
        UserLoader, BadgeLoader, PostLoader, TagLoader, PostVoteLoader, PostCommentLoader, PostHistoryLoader,
        PostLinkLoader
    )

    def __init__(self, site: str):
        """Create the importer.

        :param site: The site name.
        """
        site = models.Site.objects.get(name=site)
        self.site_id = site.pk
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
                loader = loader_class(site_id=self.site_id, data_dir=pathlib.Path(temp_dir))
                loader.load()

        # Post load actions
        self.analyze()
        siteinfo.set_site_info()

    @staticmethod
    def analyze():
        """Analyze the tables.
        """
        logger.info("Analyzing the database")
        with connection.cursor() as cursor:
            cursor.execute("ANALYZE")
        logger.info("Analyze completed")
