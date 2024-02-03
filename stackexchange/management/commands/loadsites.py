"""Command to load all site information
"""
import logging
import sys

from django.core.management.base import BaseCommand

from stackexchange import dowloader


class Command(BaseCommand):
    """Command to load all site information.
    """
    help = 'Load all site information'

    def handle(self, *args, **options):
        """Implements the logic of the command.

        :param args: The arguments.
        :param options: The options.
        """
        logging.basicConfig(
            stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')
        downloader = dowloader.Downloader(filename='Sites.xml')
        downloader.get_file()
