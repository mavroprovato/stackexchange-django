"""Command to load all available sites
"""
import logging
import sys

from django.core.management.base import BaseCommand

from sites import models, services


class Command(BaseCommand):
    """Command to load all site information.
    """
    help = 'Load all available sites'

    def handle(self, *args, **options):
        """Implements the logic of the command.

        :param args: The arguments.
        :param options: The options.
        """
        logging.basicConfig(
            stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')
        downloader = services.dowloader.Downloader(filename='Sites.xml')
        sites_file = downloader.get_file()

        logging.info("Loading sites")
        for row in services.xmlparser.XmlFileIterator(xml_file=sites_file):
            models.Site.objects.update_or_create(schema_name=row['TinyName'], defaults={
                'name': get_site_name(row['Url']), 'description': row['Name'], 'long_description': row['LongName'],
                'tagline': row['Tagline'], 'url': row['Url'], 'icon_url': row['IconUrl'],
                'badge_icon_url': row['BadgeIconUrl'], 'image_url': row['ImageUrl'], 'tag_css': row['TagCss'],
                'total_questions': row['TotalQuestions'], 'total_answers': row['TotalAnswers'],
                'total_users': row['TotalUsers'], 'total_comments': row['TotalComments'],
                'total_tags': row['TotalTags'], 'last_post_date': row['LastPost'] + '+00:00'
            })

        for site in services.xmlparser.XmlFileIterator(xml_file=sites_file):
            if 'ParentId' in site:
                models.Site.objects.filter(pk=site['Id']).update(parent=site['ParentId'])


def get_site_name(site_url: str) -> str:
    """Get the site name from the site URL.

    :param site_url: The site URL.
    :return: The site name.
    """
    return site_url.replace('https://', '').replace('.stackexchange.com', '').replace('.com', '')
