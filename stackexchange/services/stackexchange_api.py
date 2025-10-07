"""Class used to call the StackExchange API.
"""
from collections.abc import Iterable
import json
import logging
import pathlib
import time

from django.conf import settings
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
        self._cache_dir = pathlib.Path(settings.BASE_DIR) / "var" / "cache" / self.site.name
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def get_moderators(self) -> Iterable[dict]:
        """Get the users that are moderators of the site.

        :return: The user data.
        """
        logger.info("Getting moderators")

        return self._fetch_data('users/moderators')

    def get_tags(self, tag_flag: enums.TagFlag) -> Iterable[dict]:
        """Get the tags that have the specified tag flag.

        :param tag_flag: The tag flag.
        :return: The tag data.
        """
        logger.info("Getting tags with flag %s", tag_flag)

        return self._fetch_data(f"tags/{tag_flag.api_path}")

    def get_tag_synonyms(self) -> Iterable[dict]:
        """Get the tag synonyms.

        :return: The tag synonyms.
        """
        logger.info("Getting tag synonyms")

        return self._fetch_data('tags/synonyms')

    def _fetch_data(self, path: str) -> Iterable[dict]:
        """Fetch the data from the StackExchange API.

        :param path: The API path.
        :return: The data.
        """
        data = []
        if self._should_fetch(path):
            logger.info("Fetching data from API")
            data = self._fetch_data(path)
            with open(self._cache_file(path), 'wt') as file:
                json.dump(data, file)
        else:
            logger.info("Fetching data from cache")
            with open(self._cache_file(path), 'rt') as file:
                data = json.load(file)

        return data

    def _should_fetch(self, path: str) -> bool:
        """Check if a call should be performed.
        """
        if not self._cache_file(path).exists():
            return True

        return False

    def _cache_file(self, path: str) -> pathlib.Path:
        """Get the cache file.

        :param path: The API path.
        :return: The cache file.
        """
        return self._cache_dir / pathlib.Path(path.replace('/', '_') + '.json')

    def _fetch_data(self, path: str) -> Iterable[dict]:
        """Returns the data from the StackExchange API.

        :param path: The API path.
        :return: An iterable of the data returned by the StackExchange API.
        """
        url = f"{self.STACKEXCHANGE_API_BASE_URL}/{path}"
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
