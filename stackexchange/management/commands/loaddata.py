"""Command to load site data
"""
import logging
import sys

from django.core.management.base import BaseCommand, CommandParser

from stackexchange import services


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
        logging.basicConfig(
            stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')
        site = options['site']
        loader = services.loader.SiteDataLoader(site=site)
        loader.load()
