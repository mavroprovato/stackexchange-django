"""Class used to call the StackExchange API.
"""
from collections.abc import Iterable
import logging
import time

import requests

from sites import models as site_models
from stackexchange import enums

# The module logger
logger = logging.getLogger(__name__)


class StackExchangeAPI:
    """The StackExchange API class.
    """
    # The base URL of the official StackExchange API
    STACKEXCHANGE_API_BASE_URL = 'https://api.stackexchange.com/2.3'
    # The default page size
    PAGE_SIZE = 100

    def __init__(self, site: site_models.Site) -> None:
        """Initialize the StackExchange API.

        :param site: The site.
        """
        self.site = site

    def get_tags(self, tag_flag: enums.TagFlag) -> Iterable[dict]:
        """Get the tags that have the specified tag flag.

        :param tag_flag: The tag flag.
        :return: The tag data.
        """
        return self._fetch_data(f"{self.STACKEXCHANGE_API_BASE_URL}/tags/{tag_flag.api_path}")

    def _fetch_data(self, url: str) -> Iterable[dict]:
        """Returns the data from the StackExchange API.

        :param url: The endpoint URL.
        :return: An iterable of the data returned by the StackExchange API.
        """
        logger.info('Fetching data from StackExchange API url: %s', url)
        page = 1
        data = []

        while True:
            response = requests.get(
                url, params={'page': page, 'pagesize': self.PAGE_SIZE, 'site': self.site.name}, timeout=60
            )
            response.raise_for_status()
            response_data = response.json()
            data += [item for item in response_data['items']]
            if not response_data['has_more']:
                break
            page += 1
            time.sleep(1)

        return data
