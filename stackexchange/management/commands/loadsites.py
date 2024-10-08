"""Command to load all site information
"""
import logging
import sys

from django.core.management.base import BaseCommand

from stackexchange import models, services


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
        downloader = services.dowloader.Downloader(filename='Sites.xml')
        sites_file = downloader.get_file()

        logging.info("Loading sites")
        for site in services.xmlparser.XmlFileIterator(xml_file=sites_file):
            models.Site.objects.update_or_create(pk=site['Id'], defaults={
                'name': get_site_name(site['Url']), 'description': site['Name'], 'long_description': site['LongName'],
                'tagline': site['Tagline'], 'url': site['Url'], 'icon_url': site['IconUrl'],
                'badge_icon_url': site['BadgeIconUrl'], 'image_url': site['ImageUrl'], 'tag_css': site['TagCss'],
                'total_questions': site['TotalQuestions'], 'total_answers': site['TotalAnswers'],
                'total_users': site['TotalUsers'], 'total_comments': site['TotalComments'],
                'total_tags': site['TotalTags'], 'last_post_date': site['LastPost'] + '+00:00'
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
