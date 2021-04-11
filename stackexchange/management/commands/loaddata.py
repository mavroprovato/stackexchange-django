import pathlib
import re
import typing
import xml.etree.ElementTree as eT

from django.core.management.base import BaseCommand, CommandParser
from django.db import connection, transaction


class Command(BaseCommand):
    """Command to load the data from a dump directory.
    """
    help = 'Load the data from a dump directory'

    def add_arguments(self, parser: CommandParser) -> typing.NoReturn:
        """Add the command arguments.

        :param parser: The argument parser.
        """
        parser.add_argument("directory", help="The directory that contains the data to import")

    def handle(self, *args, **options):
        """Implements the logic of the command.

        :param args: The arguments.
        :param options: The options.
        :return:
        """
        import_dir = pathlib.Path(options['directory'])
        self.load_users(import_dir / "Users.xml")
        self.load_badges(import_dir / "Badges.xml")
        self.load_posts(import_dir / "Posts.xml")
        self.load_tags(import_dir / "Tags.xml", import_dir / "Posts.xml")

    def load_users(self, users_file: pathlib.Path):
        """Load the users.

        :param users_file: The users file.
        """
        self.stdout.write(f"Loading users")
        with connection.cursor() as cursor:
            with transaction.atomic():
                self.insert_data(data=self.iterate_xml(users_file), cursor=cursor, table_name='users', table_columns=(
                    'id', 'display_name', 'website', 'location', 'about', 'created', 'reputation', 'views', 'up_votes',
                    'down_votes'
                ), params=lambda row: (
                    row['Id'], row['DisplayName'], row.get('WebsiteUrl'), row.get('Location'), row.get('AboutMe'),
                    row['CreationDate'], row['Reputation'], row['Views'], row['UpVotes'], row['DownVotes']
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
            cursor.execute("SELECT id, name FROM badges")
            badges = {row[1]: row[0] for row in cursor.fetchall()}
            with transaction.atomic():
                self.insert_data(data=self.iterate_xml(badges_file), cursor=cursor, table_name='user_badges',
                                 table_columns=('badge_id', 'user_id', 'date_awarded'),
                                 params=lambda row: (
                                    badges[row['Name']], row['UserId'], row['Date']
                                 ))
        self.stdout.write(f"Badges loaded")

    def load_posts(self, posts_file: pathlib.Path):
        """Load the posts.

        :param posts_file: The posts file.
        """
        self.stdout.write(f"Loading posts")
        with connection.cursor() as cursor:
            with transaction.atomic():
                self.insert_data(data=self.iterate_xml(posts_file), cursor=cursor, table_name='posts', table_columns=(
                    'id', 'title', 'body', 'type', 'created', 'last_edit', 'last_activity', 'score', 'view_count',
                    'answer_count', 'comment_count', 'favorite_count', 'owner_id', 'last_editor_id'
                ), params=lambda row: (
                    row['Id'], row.get('Title'), row['Body'], {
                        '1': 'question', '2': 'answer', '3': 'wiki', '4': 'tag_wiki_expert', '5': 'tag_wiki',
                        '6': 'moderator_nomination', '7': 'wiki_placeholder', '8': 'privilege_wiki',
                    }[row['PostTypeId']], row['CreationDate'], row.get('LastEditDate'), row['LastActivityDate'],
                    row['Score'], row.get('ViewCount'), row.get('AnswerCount'), row.get('CommentCount'),
                    row.get('FavoriteCount'), row.get('OwnerUserId'), row.get('LastEditorUserId')
                ))
        self.stdout.write(f"Posts loaded")

    def load_tags(self, tags_file: pathlib.Path, posts_file: pathlib.Path):
        """Load the tags.

        :param tags_file: The tags file.
        :param posts_file: The posts file.
        """
        self.stdout.write(f"Loading tags")
        with connection.cursor() as cursor:
            with transaction.atomic():
                self.insert_data(data=self.iterate_xml(tags_file), cursor=cursor, table_name='tags', table_columns=(
                    'id', 'name', 'count', 'excerpt_id', 'wiki_id'
                ), params=lambda row: (
                    row['Id'], row['TagName'], row['Count'], row.get('ExcerptPostId'), row.get('WikiPostId')
                ))
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
    def insert_data(data, cursor, table_name, table_columns, params):
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        for row in data:
            cursor.execute(f"""
                INSERT INTO {table_name}({','.join(table_columns)})
                VALUES ({','.join('%s' for _ in range(len(table_columns)))})
            """, params(row))
