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


class BaseFileLoader(abc.ABC):
    """The base class for file loading.
    """
    # The filename from which to read the data. Subclasses must set this attribute.
    INPUT_FILENAME = None
    # The name of the table from which to load the data. Subclasses must set this attribute.
    TABLE_NAME = None
    # The table columns. Subclasses must set this attribute.
    TABLE_COLUMNS = None

    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Create the file loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory.
        """
        self.site_id = site_id
        self.data_dir = data_dir

    @abc.abstractmethod
    def transform(self, row: dict) -> Iterable[str] | None:
        """Transform the rows from the input file to a row that can be loaded to the database table. If an input row
        cannot be loaded, this method must return None.

        :return: The transformed row.
        """
        raise NotImplementedError

    def perform(self) -> None:
        """Load the data.
        """
        self.extract()
        self.load()

    def extract(self) -> None:
        """Extract the data from an input file.
        """
        logger.info('Extracting data from %s', self.INPUT_FILENAME)

        with self.data_filename().open('wt') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / self.INPUT_FILENAME):
                transformed_row = self.transform(row)
                if transformed_row:
                    writer.writerow(transformed_row)

    def load(self) -> None:
        """Load data for a table.
        """
        logger.info("Loading table %s", self.TABLE_NAME)

        with connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE {self.TABLE_NAME} CASCADE")
            with self.data_filename().open('rt') as f:
                cursor.copy_from(f, table=self.TABLE_NAME, columns=self.TABLE_COLUMNS, sep=',', null='<NULL>')

    def data_filename(self) -> pathlib.Path:
        """Return the file name from which to load the data.

        :return: The file name from which to load the data.
        """
        return self.data_dir / f"{self.TABLE_NAME}.csv"


class SiteUserLoader(BaseFileLoader):
    """The site user loader.
    """
    INPUT_FILENAME = 'Users.xml'
    TABLE_NAME = 'site_users'
    TABLE_COLUMNS = (
        'unique_id', 'site_id', 'display_name', 'website_url', 'location', 'about', 'creation_date',
        'last_modified_date', 'last_access_date', 'reputation', 'views', 'up_votes', 'down_votes'
    )

    def transform(self, row):
        """Transform the input row so that it can be loaded to the users table.

        :param row: The input row.
        :return: The transformed row.
        """
        return (
            row['Id'], self.site_id, row['DisplayName'], row.get('WebsiteUrl', '<NULL>'), row.get('Location', '<NULL>'),
            row.get('AboutMe', '<NULL>'), row['CreationDate'], datetime.datetime.now(), row['LastAccessDate'],
            row['Reputation'], row['Views'], row['UpVotes'], row['DownVotes']
        )


class BadgeLoader(BaseFileLoader):
    """The badge loader.
    """
    INPUT_FILENAME = 'Badges.xml'
    TABLE_NAME = 'badges'
    TABLE_COLUMNS = ('id', 'name', 'badge_class', 'badge_type')

    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Initialize the badge loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory
        """
        super().__init__(site_id, data_dir)
        self.processed_badges = set()

    def transform(self, row: dict) -> Iterable[str] | None:
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


class UserBadgeLoader(BaseFileLoader):
    """The user badge loader.
    """
    INPUT_FILENAME = 'Badges.xml'
    TABLE_NAME = 'user_badges'
    TABLE_COLUMNS = ('user_id', 'badge_id', 'date_awarded')

    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Initialize the badge loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory
        """
        super().__init__(site_id, data_dir)
        self.users = set(models.SiteUser.objects.values_list('pk', flat=True))
        self.badges = {b['name']: b['pk'] for b in models.Badge.objects.values('pk', 'name')}

    def transform(self, row: dict) -> Iterable[str] | None:
        """Transform the input row so that it can be loaded to the user_badges table.

        :param row: The input row.
        :return: The transformed row.
        """
        if int(row['UserId']) in self.users:
            return row['UserId'], self.badges[row['Name']], row['Date']

        return None


class PostLoader(BaseFileLoader):
    """The post loader.
    """
    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Initialize the post loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory
        """
        super().__init__(site_id, data_dir)
        self.users = {str(user['unique_id']): user['pk'] for user in models.SiteUser.objects.values('pk', 'unique_id')}
        self.posts = {row['Id'] for row in xmlparser.XmlFileIterator(self.data_dir / 'Posts.xml')}

    def transform_posts(self, row: dict) -> Iterable[str] | None:
        """Transform the input row so that it can be loaded to the posts table.

        :param row: The input row.
        :return: The transformed row.
        """
        return (
            row['Id'], row.get('ParentId', '<NULL>'),
            row['AcceptedAnswerId'] if row.get('AcceptedAnswerId') in self.posts else '<NULL>',
            self.users[row['OwnerUserId']] if row.get('OwnerUserId') in self.users else '<NULL>',
            self.users[row['LastEditorUserId']] if row.get('LastEditorUserId') in self.users else '<NULL>',
            row['PostTypeId'], row.get('Title', '<NULL>'), row['Body'],
            row.get('LastEditorDisplayName', '<NULL>'), row['CreationDate'], row.get('LastEditDate', '<NULL>'),
            row['LastActivityDate'], row.get('CommunityOwnedDate', '<NULL>'), row.get('ClosedDate', '<NULL>'),
            row['Score'], row.get('ViewCount', 0), row.get('AnswerCount', 0), row.get('CommentCount', 0),
            row.get('FavoriteCount', 0), row.get('ContentLicense', enums.ContentLicense.CC_BY_SA_4_0.value)
        )

    def load(self) -> None:
        """Load the posts.
        """
        self.extract_table_data(
            input_filename='Posts.xml', output_filename='posts.csv', transform_function=self.transform_posts
        )
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

    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Initialize the tag loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory
        """
        super().__init__(site_id, data_dir)
        self.tags = None

    def load(self) -> None:
        """Load the tags.
        """
        self.extract_table_data(
            input_filename='Tags.xml', output_filename='tags.csv', transform_function=self.transform_tags
        )
        self.load_table_data(
            filename='tags.csv', table_name='tags', columns=(
                'id', 'name', 'award_count', 'excerpt_id', 'wiki_id', 'required', 'moderator_only'
            )
        )

        self.update_tag_flags()

        self.tags = {t['name']: t['pk'] for t in models.Tag.objects.values('pk', 'name')}
        logger.info("Extracting post tags")
        with (self.data_dir / 'post_tags.csv').open('wt') as post_tags_file:
            post_tags_writer = csv.writer(post_tags_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row in xmlparser.XmlFileIterator(self.data_dir / 'Posts.xml'):
                for tag_name in row.get('Tags', '').split('|'):
                    if tag_name and tag_name in self.tags:
                        post_tags_writer.writerow([row['Id'], self.tags[tag_name]])
        self.load_table_data(filename='post_tags.csv', table_name='post_tags', columns=('post_id', 'tag_id'))

    @staticmethod
    def transform_tags(row: dict) -> Iterable[str] | None:
        """Transform the input row so that it can be loaded to the tags table.

        :param row: The input row.
        :return: The transformed row.
        """
        return (
            row['Id'], row['TagName'], row['Count'], row.get('ExcerptPostId', '<NULL>'),
            row.get('WikiPostId', '<NULL>'), row.get('IsRequired') == 'True', row.get('ModeratorOnly') == 'True'
        )

    def update_tag_flags(self) -> None:
        """Update the flags (required and moderator only) from the stack exchange API.
        """
        logger.info("Updating tag flags")
        for tag_flag in enums.TagFlag:
            tag_names = self.get_tag_names(tag_flag)
            for tag_name in tag_names:
                tag = models.Tag.objects.filter(name=tag_name).first()
                if tag is not None:
                    setattr(tag, tag_flag.attribute_name, True)
                    tag.save()

    def get_tag_names(self, tag_flag: enums.TagFlag) -> Iterable[str]:
        """Returns the names of the tags that have the given flag.

        :param tag_flag: The tag flag.
        :return: An iterable of tag names that have the given flag set.
        """
        page = 1
        tags = []

        site = models.Site.objects.get(pk=self.site_id)
        while True:
            response = requests.get(
                f"{self.STACKEXCHANGE_API_BASE_URL}/tags/{tag_flag.api_path}",
                params={'page': page, 'pagesize': 100, 'site': site.name}, timeout=60
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
    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Initialize the post vote loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory
        """
        super().__init__(site_id, data_dir)
        self.posts = set(models.Post.objects.values_list('pk', flat=True))
        self.users = {user['unique_id']: user['pk'] for user in models.SiteUser.objects.values('pk', 'unique_id')}

    def load(self) -> None:
        """Load the post votes.
        """
        self.extract_table_data(
            input_filename='Votes.xml', output_filename='post_votes.csv', transform_function=self.transform_post_votes
        )
        self.load_table_data(
            filename='post_votes.csv', table_name='post_votes', columns=(
                'id', 'post_id', 'type', 'creation_date', 'user_id', 'bounty_amount'
            )
        )

    def transform_post_votes(self, row: dict) -> Iterable[str] | None:
        """Transform the input row so that it can be loaded to the post votes table.

        :param row: The input row.
        :return: The transformed row.
        """
        if int(row['PostId']) in self.posts:
            return (
                row['Id'], row['PostId'], row['VoteTypeId'], row['CreationDate'],
                self.users[row['UserId']] if row.get('UserId') in self.users else '<NULL>',
                row.get('BountyAmount', '<NULL>')
            )

        return None


class PostCommentLoader(BaseFileLoader):
    """The post comment loader.
    """
    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Initialize the post comment loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory
        """
        super().__init__(site_id, data_dir)
        self.users = {user['unique_id']: user['pk'] for user in models.SiteUser.objects.values('pk', 'unique_id')}

    def load(self) -> None:
        """Load the post comments.
        """
        self.extract_table_data(
            input_filename='Comments.xml', output_filename='post_comments.csv',
            transform_function=self.transform_post_comments
        )
        self.load_table_data(
            filename='post_comments.csv', table_name='post_comments', columns=(
                'id', 'post_id', 'score', 'text', 'creation_date', 'content_license', 'user_id', 'user_display_name'
            )
        )

    def transform_post_comments(self, row: dict) -> Iterable[str] | None:
        """Transform the input row so that it can be loaded to the post comments table.

        :param row: The input row.
        :return: The transformed row.
        """
        return (
            row['Id'], row['PostId'], row['Score'], row['Text'], row['CreationDate'],
            row.get('ContentLicense', enums.ContentLicense.CC_BY_SA_4_0.value),
            self.users[row['UserId']] if row.get('UserId') in self.users else '<NULL>',
            row.get('UserDisplayName', '<NULL>')
        )


class PostHistoryLoader(BaseFileLoader):
    """The post history loader.
    """
    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Initialize the post history loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory
        """
        super().__init__(site_id, data_dir)
        self.posts = set(models.Post.objects.values_list('pk', flat=True))
        self.users = {user['unique_id']: user['pk'] for user in models.SiteUser.objects.values('pk', 'unique_id')}

    def load(self) -> None:
        """Load the post history.
        """
        self.extract_table_data(
            input_filename='PostHistory.xml', output_filename='post_history.csv',
            transform_function=self.transform_post_history
        )
        self.load_table_data(
            filename='post_history.csv', table_name='post_history', columns=(
                'id', 'type', 'post_id', 'revision_guid', 'creation_date', 'user_id', 'user_display_name', 'comment',
                'text', 'content_license'
            )
        )

    def transform_post_history(self, row: dict) -> Iterable[str] | None:
        """Transform the input row so that it can be loaded to the tags table.

        :param row: The input row.
        :return: The transformed row.
        """
        if int(row['PostId']) in self.posts:
            return (
                row['Id'], row['PostHistoryTypeId'], row['PostId'], row['RevisionGUID'], row['CreationDate'],
                self.users[row['UserId']] if row.get('UserId') in self.users else '<NULL>',
                row.get('UserDisplayName', '<NULL>'), row.get('Comment', '<NULL>'),
                row.get('Text', '<NULL>'), row.get('ContentLicense', enums.ContentLicense.CC_BY_SA_4_0.value)
            )

        return None


class PostLinkLoader(BaseFileLoader):
    """The post link loader.
    """
    def __init__(self, site_id: int, data_dir: pathlib.Path) -> None:
        """Initialize the post link loader.

        :param site_id: The site identifier.
        :param data_dir: The data directory
        """
        super().__init__(site_id, data_dir)
        self.posts = set(models.Post.objects.values_list('pk', flat=True))

    def load(self) -> None:
        """Load the post links.
        """
        self.extract_table_data(
            input_filename='PostLinks.xml', output_filename='post_links.csv',
            transform_function=self.transform_post_history
        )
        self.load_table_data(
            filename='post_links.csv', table_name='post_links', columns=('id', 'post_id', 'related_post_id', 'type')
        )

    def transform_post_history(self, row: dict) -> Iterable[str] | None:
        """Transform the input row so that it can be loaded to the tags table.

        :param row: The input row.
        :return: The transformed row.
        """
        if int(row['PostId']) in self.posts and int(row['RelatedPostId']) in self.posts:
            return row['Id'], row['PostId'], row['RelatedPostId'], row['LinkTypeId']

        return None


class SiteDataLoader:
    """Helper class to load site data
    """
    LOADERS = (
        SiteUserLoader, BadgeLoader, UserBadgeLoader
        # , PostLoader, TagLoader, PostVoteLoader, PostCommentLoader,
        # PostHistoryLoader, PostLinkLoader
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
                loader.perform()

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
